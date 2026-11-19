"""Paths supplied by the command-line runner to each rendering stage."""
import os
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"
INPUTS = Path(os.environ["MTS_2022_SOURCES"])
WORK = Path(os.environ["MTS_2022_WORK"])
OUTPUT = Path(os.environ["MTS_2022_OUTPUT"])

def source(subject, grade):
    return INPUTS / f"NY_{subject}_Grade{grade}_2022_Released_Test_Questions.pdf"
