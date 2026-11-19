import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from mts.products.mock_assessment.grade4_student import _validated_page_breaks


def test_accepts_breaks_for_selected_items():
    assert _validated_page_breaks([42], [41, 42, 43]) == [42]


@pytest.mark.parametrize("value", [None, "42", [True], [[42]], [99], [42, 42]])
def test_rejects_invalid_page_breaks(value):
    with pytest.raises(ValueError, match="unique selected item IDs"):
        _validated_page_breaks(value, [41, 42, 43])
