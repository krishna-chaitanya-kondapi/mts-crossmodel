"""Fail-closed development verification gate; not a semantic verifier."""
from pathlib import Path
import hashlib

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def evaluate(registry, report, root, revision, registry_hash):
    """Return gate result. PASS evidence must be local, hashed and revision-bound."""
    criteria = registry["criteria"]
    ids = [c["id"] for c in criteria]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError("Invalid registry IDs")
    records = report.get("criteria", [])
    by_id = {r["id"]: r for r in records}
    if len(by_id) != len(records) or set(by_id) - set(ids):
        raise ValueError("Duplicate or unknown report criteria")
    current = report.get("revision") == revision and report.get("registry_sha256") == registry_hash
    root = Path(root).resolve()
    results = []
    for c in criteria:
        r = by_id.get(c["id"], {})
        status = r.get("status", "NOT_VERIFIED")
        if status not in {"PASS", "FAIL", "BLOCKED", "NOT_VERIFIED", "NOT_APPLICABLE", "WAIVED"}:
            raise ValueError("Unknown status")
        if status == "PASS":
            evidence = r.get("evidence", [])
            valid = current and bool(evidence) and all(r.get(k) for k in ("method", "reviewer", "expected", "actual"))
            for e in evidence:
                p = (root / e["path"]).resolve()
                valid = valid and p.is_relative_to(root) and p.is_file() and digest(p) == e.get("sha256")
            if not valid:
                status = "NOT_VERIFIED"
        results.append({"id": c["id"], "mandatory": c["mandatory"], "status": status})
    pending = [r["id"] for r in results if r["mandatory"] and r["status"] != "PASS"]
    return {"status": "NOT_DONE" if pending or not current else "READY_FOR_ACCEPTANCE",
            "revision": revision, "criteria": results, "pending_mandatory": pending}
