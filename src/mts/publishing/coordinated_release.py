"""Coordinate flat local publication while preserving unrelated approved files."""

from hashlib import sha256
import os
from pathlib import Path
import shutil
import tempfile


def publish_verified_files(files, destination, *, expected_hashes, replace_hashes=None):
    """Publish an explicitly named set under a shared lock, rolling back failures."""
    destination = Path(destination).resolve()
    replace_hashes = replace_hashes or {}
    if not files or set(files) != set(expected_hashes):
        raise ValueError("Every release file needs exactly one expected fingerprint")
    for name, source in files.items():
        if (
            Path(name).name != name
            or "/" in name
            or "\\" in name
            or not name.lower().endswith(".pdf")
        ):
            raise ValueError("Release names must be flat PDF filenames")
        if sha256(Path(source).read_bytes()).hexdigest() != expected_hashes[name]:
            raise ValueError(f"Release file changed: {name}")
    destination.mkdir(parents=True, exist_ok=True)
    lock = destination / ".mts-publication.lock"
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.close(descriptor)
    replaced = []
    try:
        baseline = {
            p.name: sha256(p.read_bytes()).hexdigest()
            for p in destination.glob("*.pdf")
        }
        for name in files:
            if name in baseline and replace_hashes.get(name) != baseline[name]:
                raise ValueError(f"Replacement of {name} needs its prior fingerprint")
        stage = Path(tempfile.mkdtemp(prefix=".release-", dir=destination))
        preserve_backups = False
        try:
            for name, source in files.items():
                shutil.copy2(source, stage / name)
                if (
                    sha256((stage / name).read_bytes()).hexdigest()
                    != expected_hashes[name]
                ):
                    raise ValueError(f"Staged file changed: {name}")
            try:
                for name in files:
                    target = destination / name
                    backup = stage / (name + ".previous")
                    if target.exists():
                        shutil.copy2(target, backup)
                    os.replace(stage / name, target)
                    replaced.append((target, backup))
                for name, expected in expected_hashes.items():
                    if (
                        sha256((destination / name).read_bytes()).hexdigest()
                        != expected
                    ):
                        raise ValueError(f"Published readback failed: {name}")
                for name, expected in baseline.items():
                    if (
                        name not in files
                        and sha256((destination / name).read_bytes()).hexdigest()
                        != expected
                    ):
                        raise ValueError(f"Unrelated approved file changed: {name}")
            except Exception as failure:
                try:
                    for target, backup in reversed(replaced):
                        if backup.exists():
                            os.replace(backup, target)
                        else:
                            target.unlink()
                except Exception as recovery_error:
                    preserve_backups = True
                    raise RuntimeError(
                        f"Local publication needs recovery; prior approved backups retained in {stage}: {recovery_error}"
                    ) from failure
                raise
        finally:
            if not preserve_backups:
                shutil.rmtree(stage)
        return {
            "published": dict(expected_hashes),
            "preserved": {n: h for n, h in baseline.items() if n not in files},
        }
    finally:
        lock.unlink()
