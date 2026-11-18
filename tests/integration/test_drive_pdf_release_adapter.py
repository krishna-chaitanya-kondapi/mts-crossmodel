"""Wire-level tests for the neutral Drive PDF upload and inventory extensions."""

from pathlib import Path
import sys
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from mts.infrastructure.google_docs.google_docs_adapter import GoogleDocsAdapter


def test_pdf_upload_keeps_pdf_type_and_operation_identity(tmp_path):
    source = tmp_path / "review.pdf"
    source.write_bytes(b"%PDF-1.7 test")
    drive = Mock()
    drive.files.return_value.create.return_value.execute.return_value = {
        "id": "uploaded",
        "name": "review.pdf",
    }
    adapter = GoogleDocsAdapter(drive, None)
    result = adapter.upload_pdf(
        source, "archive", "review.pdf", properties={"mts_release_operation": "op"}
    )
    request = drive.files.return_value.create.call_args.kwargs
    assert request["body"] == {
        "name": "review.pdf",
        "parents": ["archive"],
        "mimeType": "application/pdf",
        "appProperties": {"mts_release_operation": "op"},
    }
    assert request["media_body"].mimetype() == "application/pdf"
    assert result["id"] == "uploaded"


def test_release_inventory_preserves_provider_pagination_and_identity_fields():
    drive = Mock()
    drive.files.return_value.list.return_value.execute.side_effect = [
        {"files": [{"id": "first"}], "nextPageToken": "next"},
        {"files": [{"id": "second"}]},
    ]
    adapter = GoogleDocsAdapter(drive, None)
    assert [item["id"] for item in adapter.release_inventory("ready")] == [
        "first",
        "second",
    ]
    calls = drive.files.return_value.list.call_args_list
    assert "md5Checksum" in calls[0].kwargs["fields"]
    assert "parents" in calls[0].kwargs["fields"]
    assert calls[1].kwargs["pageToken"] == "next"
