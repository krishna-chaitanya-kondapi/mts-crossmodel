"""Publish a PDF set through Drive with durable operation records and recovery."""

from hashlib import sha256
import json
import os
from pathlib import Path
from uuid import uuid4

from mts.infrastructure.file_system.atomic_writer import write_json


def _restore_prior_set(record, adapter):
    destination = record["destination_id"]
    archive = record["archive_id"]
    operation = record["operation_id"]
    created = {item["id"]: item for item in record["staged"]}
    errors = []
    for folder in (archive, destination):
        try:
            for item in adapter.release_inventory(folder):
                if (
                    item.get("appProperties", {}).get("mts_release_operation")
                    == operation
                ):
                    created[item["id"]] = item
        except Exception as error:
            errors.append(str(error))
    for identity in created:
        try:
            adapter.trash_file(identity)
        except Exception as error:
            errors.append(str(error))
    for old in record["attempted_predecessors"]:
        try:
            actual = sha256(adapter.export_pdf(old["id"])).hexdigest()
            if actual != record["replace_hashes"][old["name"]]:
                raise ValueError("Archived predecessor changed after approval")
            adapter.move_file(old["id"], destination)
        except Exception as error:
            errors.append(str(error))
    if errors:
        raise RuntimeError("; ".join(errors))
    final = {item["id"]: item for item in adapter.release_inventory(destination)}
    if any(identity not in final for identity in record["baseline"]):
        raise RuntimeError("Prior approved set is incomplete after recovery")
    if set(created) & set(final):
        raise RuntimeError("A failed candidate remains in PrintReady after recovery")


def recover_drive_publication(journal_path, adapter):
    """Recover one interrupted operation using only recorded and operation-tagged IDs."""
    journal_path = Path(journal_path)
    record = json.loads(journal_path.read_text(encoding="utf-8-sig"))
    if record["status"] not in {"RUNNING", "RECOVERY_REQUIRED"}:
        raise ValueError("This publication operation needs no recovery")
    lock = Path(record["lock_path"])
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.close(descriptor)
    try:
        _restore_prior_set(record, adapter)
        record["status"] = "ROLLED_BACK"
        write_json(journal_path, record)
        return record
    except Exception as error:
        record.update(status="RECOVERY_REQUIRED", recovery_error=str(error))
        write_json(journal_path, record)
        raise
    finally:
        lock.unlink()


def publish_verified_drive_files(
    files,
    destination_id,
    archive_id,
    adapter,
    *,
    expected_hashes,
    lock_path,
    replace_hashes=None,
):
    if not destination_id or not archive_id or destination_id == archive_id:
        raise ValueError("Distinct PrintReady and archive folder IDs are required")
    if set(files) != set(expected_hashes) or not files:
        raise ValueError("Every publication file needs an exact fingerprint")
    for name, source in files.items():
        if (
            Path(name).name != name
            or "/" in name
            or "\\" in name
            or not name.endswith(".pdf")
        ):
            raise ValueError("Publication names must be flat PDF names")
        if sha256(Path(source).read_bytes()).hexdigest() != expected_hashes[name]:
            raise ValueError(f"Approved source changed: {name}")
    lock = Path(lock_path).resolve()
    lock.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.close(descriptor)
    operation = uuid4().hex
    journals = lock.parent / ".publication-journals"
    journal_path = journals / (operation + ".json")
    record = None
    try:
        for path in journals.glob("*.json"):
            prior = json.loads(path.read_text(encoding="utf-8-sig"))
            if prior["destination_id"] == destination_id and prior["status"] in {
                "RUNNING",
                "RECOVERY_REQUIRED",
            }:
                raise ValueError(f"Recover the previous publication first: {path}")
        baseline = {
            item["id"]: item for item in adapter.release_inventory(destination_id)
        }
        previous = []
        replace_hashes = replace_hashes or {}
        for name in files:
            matches = [item for item in baseline.values() if item["name"] == name]
            if len(matches) > 1:
                raise ValueError(f"Ambiguous existing publication name: {name}")
            if matches:
                old = matches[0]
                actual = sha256(adapter.export_pdf(old["id"])).hexdigest()
                if replace_hashes.get(name) != actual:
                    raise ValueError(f"Replacement needs prior fingerprint: {name}")
                previous.append(old)
        record = {
            "operation_id": operation,
            "status": "RUNNING",
            "lock_path": str(lock),
            "destination_id": destination_id,
            "archive_id": archive_id,
            "baseline": baseline,
            "predecessors": previous,
            "replace_hashes": replace_hashes,
            "expected_hashes": expected_hashes,
            "staged": [],
            "attempted_predecessors": [],
        }
        write_json(journal_path, record)
        try:
            for name, path in files.items():
                created = adapter.upload_pdf(
                    path,
                    archive_id,
                    name,
                    properties={"mts_release_operation": operation},
                )
                record["staged"].append(created)
                write_json(journal_path, record)
                if (
                    sha256(adapter.export_pdf(created["id"])).hexdigest()
                    != expected_hashes[name]
                ):
                    raise ValueError(f"Staged Drive readback failed: {name}")
            current = {
                item["id"]: item for item in adapter.release_inventory(destination_id)
            }
            for old in previous:
                if (
                    old["id"] not in current
                    or current[old["id"]]["name"] != old["name"]
                ):
                    raise ValueError("An approved predecessor moved during staging")
            for old in previous:
                record["attempted_predecessors"].append(old)
                write_json(journal_path, record)
                adapter.move_file(old["id"], archive_id)
            for new in record["staged"]:
                adapter.move_file(new["id"], destination_id)
            final = {
                item["id"]: item for item in adapter.release_inventory(destination_id)
            }
            old_ids = {item["id"] for item in previous}
            for new in record["staged"]:
                same_name = [
                    item for item in final.values() if item["name"] == new["name"]
                ]
                if len(same_name) != 1 or same_name[0]["id"] != new["id"]:
                    raise ValueError("Publication name collided during commit")
                if (
                    sha256(adapter.export_pdf(new["id"])).hexdigest()
                    != expected_hashes[new["name"]]
                ):
                    raise ValueError("Published PDF readback failed")
            for identity, old in baseline.items():
                if identity in old_ids:
                    continue
                if identity not in final:
                    raise ValueError("An unrelated approved file disappeared")
                for key in ["name", "mimeType", "md5Checksum", "size", "version"]:
                    if old.get(key) != final[identity].get(key):
                        raise ValueError("An unrelated approved file changed")
            archived = {
                item["id"]: item for item in adapter.release_inventory(archive_id)
            }
            if any(item["id"] not in archived for item in previous):
                raise ValueError("An approved predecessor was not archived")
            receipt = {
                "published": [final[item["id"]] for item in record["staged"]],
                "archived": [archived[item["id"]] for item in previous],
                "preserved_ids": sorted(set(baseline) - old_ids),
                "operation_id": operation,
                "journal_path": str(journal_path),
            }
            record.update(status="COMMITTED", receipt=receipt)
            write_json(journal_path, record)
            return receipt
        except Exception as failure:
            try:
                _restore_prior_set(record, adapter)
                record.update(status="ROLLED_BACK", error=str(failure))
                write_json(journal_path, record)
            except Exception as recovery_error:
                record.update(
                    status="RECOVERY_REQUIRED",
                    error=str(failure),
                    recovery_error=str(recovery_error),
                )
                write_json(journal_path, record)
                raise RuntimeError(
                    f"Drive publication needs recovery from {journal_path}"
                ) from failure
            raise
    finally:
        lock.unlink()
