# Reproduce the 2022 Grades 4–6 review packets

This is the run-specific entry point for the six 2022 Math and ELA assessments. The historical-profile CLI remains in [scripts/generate_mock_assessment.py](../../../scripts/generate_mock_assessment.py). Consult the [source-use ledger](../source-use.md) before selecting assessment sources.

## Inputs and dependencies

- Python 3.12, the pinned dependencies in `requirements.txt`, and Poppler `pdftotext` (tested with 25.03.0).
- Nimbus Roman regular and bold OpenType files. Point `--font-dir` to the folder containing `NimbusRoman-Regular.otf` and `NimbusRoman-Bold.otf`.
- Obtain the six original PDF files using the Drive IDs in [sources.json](data/sources.json). Save them under their exact listed filenames in one directory. The runner checks each SHA-256 before rendering. The source PDFs remain in the authorized source store.
- The ELA selection and scoring manifests live in `data/`. Math item selection and worked solutions are in `run_compact.py`.

From the repository root:

```sh
python -m pip install -r specs/generate_mock_assessment/ny2022/requirements.txt
python specs/generate_mock_assessment/ny2022/run.py \
  --sources /path/to/original-pdfs \
  --font-dir /path/to/nimbus-roman-fonts \
  --output /path/to/new-review-output
```

The command extracts source text, renders the student booklets and teacher keys, checks ordered selections, page counts, PDF geometry and ELA scoring, then writes per-grade evidence and `artifacts.json` with file hashes. It uses a fresh temporary work directory and accepts a new or empty output directory. PDF metadata can change between runs, so use rendered-page comparisons for layout equivalence. Human academic, print and release review remain workflow checkpoints.
