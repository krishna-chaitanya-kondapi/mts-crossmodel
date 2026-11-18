"""Read NYSED released-test item maps from layout-preserving PDF text."""
import re

_ITEM = re.compile(
    r"^\s*(?P<number>[1-9]\d*)\s+(?P<kind>Multiple Choice|Constructed Response)"
    r"\s+(?P<key>[A-Z]|n/a)\s+(?P<points>[1-9]\d*)"
    r"\s+(?P<standard>NGLS\.\S+)"
)


def select_items(item_map_text, source_numbers, *, renumber=False):
    """Bind a historical selection to official keys, points, and standards."""
    if not source_numbers or list(source_numbers) != sorted(set(source_numbers)):
        raise ValueError("Source item numbers must be nonempty, unique, and in order")

    selected = set(source_numbers)
    official = {}
    for line in item_map_text.splitlines():
        match = _ITEM.match(line)
        if not match:
            continue
        number = int(match["number"])
        if number not in selected:
            continue
        if number in official:
            raise ValueError(f"Duplicate official item-map row for source question {number}")
        multiple_choice = match["kind"] == "Multiple Choice"
        key = match["key"]
        if multiple_choice == (key == "n/a"):
            raise ValueError(f"Inconsistent official key for source question {number}")
        official[number] = {
            "source_number": number,
            "type": "multiple_choice" if multiple_choice else "constructed_response",
            "official_key": key if multiple_choice else None,
            "points": int(match["points"]),
            "standard": match["standard"],
        }

    missing = sorted(selected - official.keys())
    if missing:
        raise ValueError(f"No official item-map rows for source questions {missing}")

    return [
        dict(official[number], output_number=index if renumber else number)
        for index, number in enumerate(source_numbers, 1)
    ]
