"""Official item-map selection regression tests."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))

from mts.products.mock_assessment.item_map import select_items


ITEM_MAP = """
    8   Multiple Choice        B    1   NGLS.ELA.Content.NY-6.R.3    Reading
   27   Constructed Response n/a    2   NGLS.ELA.Content.NY-6.R.2    Writing
"""


def test_selects_official_scoring_and_keeps_source_identity():
    first, second = select_items(ITEM_MAP, [8, 27], renumber=True)
    assert first == {
        "source_number": 8, "output_number": 1, "type": "multiple_choice",
        "official_key": "B", "points": 1, "standard": "NGLS.ELA.Content.NY-6.R.3",
    }
    assert second["output_number"] == 2
    assert second["official_key"] is None
    assert second["points"] == 2
    assert select_items(ITEM_MAP, [27])[0]["output_number"] == 27


@pytest.mark.parametrize(("text", "selection", "error"), [
    (ITEM_MAP, [8, 8], "unique"),
    (ITEM_MAP, [9], "No official"),
    (ITEM_MAP + ITEM_MAP, [8], "Duplicate"),
    (ITEM_MAP.replace("B    1", "n/a  1"), [8], "Inconsistent"),
])
def test_rejects_incomplete_or_ambiguous_selections(text, selection, error):
    with pytest.raises(ValueError, match=error):
        select_items(text, selection)

