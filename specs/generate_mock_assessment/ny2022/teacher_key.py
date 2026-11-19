"""Render a local Math teacher key from official item metadata and worked solutions."""
import math


def render_teacher_key(items, solutions, destination, *, title):
    """Render ordered answers and credit values for a source-based assessment."""
    import pymupdf

    numbers = [item["output_number"] for item in items]
    if not numbers or len(numbers) != len(set(numbers)):
        raise ValueError("Teacher key requires unique worksheet numbers")
    constructed = {
        str(item["output_number"]) for item in items
        if item["type"] == "constructed_response"
    }
    if set(solutions) != constructed or any(not value.strip() for value in solutions.values()):
        raise ValueError("Every constructed response needs exactly one worked solution")

    multiple_choice = []
    worked = []
    for item in items:
        number = item["output_number"]
        points = item["points"]
        if type(points) is not int or points < 1:
            raise ValueError(f"Invalid credit value for question {number}")
        if item["type"] == "multiple_choice" and item["official_key"] in ("A", "B", "C", "D"):
            multiple_choice.append(f"{number}: {item['official_key']}")
        elif item["type"] == "constructed_response" and item["official_key"] is None:
            worked.append(f"{number} ({points} {'credit' if points == 1 else 'credits'})  {solutions[str(number)]}")
        else:
            raise ValueError(f"Invalid official key for question {number}")

    font = pymupdf.Font("helv")
    lines = ["Multiple-choice answers"]
    for index in range(0, len(multiple_choice), 7):
        lines.append("     ".join(multiple_choice[index:index + 7]))
    lines.extend(["", "Constructed responses - MTS worked solutions", ""])
    size = 10
    for solution in worked:
        line = ""
        for word in solution.split():
            candidate = f"{line} {word}".strip()
            if font.text_length(candidate, fontsize=size) <= 528:
                line = candidate
            elif line:
                lines.append(line)
                line = word
            else:
                raise ValueError("A worked solution has an unbreakable line")
        lines.extend([line, ""])

    line_height = 14
    if math.ceil(92 + len(lines) * line_height) > 745:
        raise ValueError("Teacher key exceeds its single-page layout")
    with pymupdf.open() as pdf:
        page = pdf.new_page(width=612, height=792)
        page.insert_text((42, 48), title, fontsize=15, fontname="hebo")
        page.insert_text((42, 68), "Teacher review copy", fontsize=9)
        for index, line in enumerate(lines):
            page.insert_text((42, 92 + index * line_height), line, fontsize=size)
        pdf.save(destination, garbage=4, deflate=True)
