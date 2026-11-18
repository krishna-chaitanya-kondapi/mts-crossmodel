"""Drive PrintReady preservation, archival, readback and recovery tests."""

from copy import deepcopy
import json
from hashlib import md5, sha256
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from mts.publishing.coordinated_drive_release import (
    publish_verified_drive_files,
    recover_drive_publication,
)


class DriveStore:
    def __init__(self):
        self.files = {}
        self.next_id = 0
        self.fail_move_number = None
        self.moves = 0
        self.lose_upload_response = False

    def add(self, name, data, parent, properties=None):
        self.next_id += 1
        identity = str(self.next_id)
        self.files[identity] = {
            "id": identity,
            "name": name,
            "mimeType": "application/pdf",
            "parents": [parent],
            "md5Checksum": md5(data).hexdigest(),
            "size": str(len(data)),
            "appProperties": properties or {},
            "data": data,
            "trashed": False,
        }
        return identity

    def release_inventory(self, folder):
        return [
            deepcopy({k: v for k, v in value.items() if k not in {"data", "trashed"}})
            for value in self.files.values()
            if not value["trashed"] and folder in value["parents"]
        ]

    def export_pdf(self, identity):
        return self.files[identity]["data"]

    def upload_pdf(self, path, folder, name, properties=None):
        identity = self.add(name, Path(path).read_bytes(), folder, properties)
        if self.lose_upload_response:
            self.lose_upload_response = False
            raise OSError("lost upload response")
        return deepcopy(
            {
                k: v
                for k, v in self.files[identity].items()
                if k not in {"data", "trashed"}
            }
        )

    def move_file(self, identity, folder):
        self.moves += 1
        self.files[identity]["parents"] = [folder]
        if self.moves == self.fail_move_number:
            raise OSError("lost move response")
        return self.files[identity]

    def trash_file(self, identity):
        self.files[identity]["trashed"] = True


@pytest.fixture
def storage_case(tmp_path):
    adapter = DriveStore()
    weekly = adapter.add("weekly.pdf", b"approved weekly", "ready")
    other = adapter.add("other-subject.pdf", b"approved other", "ready")
    files = {}
    hashes = {}
    for name in ("mock-student.pdf", "mock-teacher.pdf"):
        path = tmp_path / name
        path.write_bytes(b"%PDF-1.7 " + name.encode())
        files[name] = path
        hashes[name] = sha256(path.read_bytes()).hexdigest()
    return adapter, weekly, other, files, hashes, tmp_path / "publish.lock"


def test_drive_publication_preserves_other_approved_artifacts(storage_case):
    adapter, weekly, other, files, hashes, lock = storage_case
    baseline = deepcopy(adapter.files)
    result = publish_verified_drive_files(
        files, "ready", "archive", adapter, expected_hashes=hashes, lock_path=lock
    )
    assert result["preserved_ids"] == sorted([weekly, other])
    assert adapter.files[weekly] == baseline[weekly]
    assert adapter.files[other] == baseline[other]
    assert len(adapter.release_inventory("ready")) == 4
    assert all(item["parents"] == ["ready"] for item in result["published"])
    assert not lock.exists()


def test_prior_approved_pdf_is_archived_under_same_identity(storage_case):
    adapter, _, _, files, hashes, lock = storage_case
    identity = adapter.add("mock-student.pdf", b"older approved", "ready")
    previous = sha256(b"older approved").hexdigest()
    result = publish_verified_drive_files(
        files,
        "ready",
        "archive",
        adapter,
        expected_hashes=hashes,
        replace_hashes={"mock-student.pdf": previous},
        lock_path=lock,
    )
    assert adapter.files[identity]["parents"] == ["archive"]
    assert adapter.files[identity]["data"] == b"older approved"
    assert result["archived"][0]["id"] == identity
    assert result["archived"][0]["parents"] == ["archive"]


def test_unknown_existing_version_is_never_overwritten(storage_case):
    adapter, _, _, files, hashes, lock = storage_case
    identity = adapter.add("mock-student.pdf", b"unknown prior", "ready")
    with pytest.raises(ValueError, match="prior fingerprint"):
        publish_verified_drive_files(
            files, "ready", "archive", adapter, expected_hashes=hashes, lock_path=lock
        )
    assert adapter.files[identity]["parents"] == ["ready"]
    assert adapter.release_inventory("archive") == []


def test_lost_move_response_restores_original_and_removes_only_new_files(storage_case):
    adapter, weekly, other, files, hashes, lock = storage_case
    identity = adapter.add("mock-student.pdf", b"prior approved", "ready")
    adapter.fail_move_number = 2
    with pytest.raises(OSError, match="lost move"):
        publish_verified_drive_files(
            files,
            "ready",
            "archive",
            adapter,
            expected_hashes=hashes,
            replace_hashes={"mock-student.pdf": sha256(b"prior approved").hexdigest()},
            lock_path=lock,
        )
    assert {item["id"] for item in adapter.release_inventory("ready")} == {
        weekly,
        other,
        identity,
    }
    assert adapter.files[identity]["data"] == b"prior approved"
    assert not lock.exists()


def test_lost_upload_response_is_recovered_by_operation_identity(storage_case):
    adapter, weekly, other, files, hashes, lock = storage_case
    adapter.lose_upload_response = True
    with pytest.raises(OSError, match="lost upload"):
        publish_verified_drive_files(
            files, "ready", "archive", adapter, expected_hashes=hashes, lock_path=lock
        )
    assert {item["id"] for item in adapter.release_inventory("ready")} == {
        weekly,
        other,
    }
    assert adapter.release_inventory("archive") == []


def test_shared_lock_blocks_concurrent_publication(storage_case):
    adapter, _, _, files, hashes, lock = storage_case
    lock.write_text("another publisher")
    with pytest.raises(FileExistsError):
        publish_verified_drive_files(
            files, "ready", "archive", adapter, expected_hashes=hashes, lock_path=lock
        )
    assert lock.read_text() == "another publisher"
    assert len(adapter.files) == 2


def test_persistent_outage_can_be_recovered_from_durable_journal(storage_case):
    adapter, weekly, other, files, hashes, lock = storage_case
    identity = adapter.add("mock-student.pdf", b"prior approved", "ready")
    original_move = adapter.move_file
    original_inventory = adapter.release_inventory
    outage = {"active": False}

    def interrupted_move(file_id, folder):
        result = original_move(file_id, folder)
        outage["active"] = True
        raise OSError("persistent network outage")

    def unavailable_inventory(folder):
        if outage["active"]:
            raise OSError("persistent network outage")
        return original_inventory(folder)

    adapter.move_file = interrupted_move
    adapter.release_inventory = unavailable_inventory
    with pytest.raises(RuntimeError, match="needs recovery"):
        publish_verified_drive_files(
            files,
            "ready",
            "archive",
            adapter,
            expected_hashes=hashes,
            replace_hashes={"mock-student.pdf": sha256(b"prior approved").hexdigest()},
            lock_path=lock,
        )
    journal = next((lock.parent / ".publication-journals").glob("*.json"))
    assert json.loads(journal.read_text())["status"] == "RECOVERY_REQUIRED"
    assert not lock.exists()
    adapter.move_file = original_move
    adapter.release_inventory = original_inventory
    recovered = recover_drive_publication(journal, adapter)
    assert recovered["status"] == "ROLLED_BACK"
    assert {item["id"] for item in adapter.release_inventory("ready")} == {
        weekly,
        other,
        identity,
    }
    assert adapter.files[identity]["data"] == b"prior approved"
    assert adapter.release_inventory("archive") == []
    with pytest.raises(ValueError, match="needs no recovery"):
        recover_drive_publication(journal, adapter)
