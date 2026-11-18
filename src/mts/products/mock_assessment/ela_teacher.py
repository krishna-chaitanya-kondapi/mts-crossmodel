"""Render the recovered ELA YPQA teacher content for local review."""
import re


_PUNCTUATION = str.maketrans({
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2013": "-",
    "\u2014": "-",
    "\u2022": "|",
    "\u2026": "...",
    "\u00a0": " ",
})


def _wrap(text, width, font, size):
    lines = []
    line = ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if line and font.text_length(candidate, fontsize=size) > width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def _paragraph_lines(text, width, regular, bold, size):
    label, separator, remainder = text.partition(":")
    if not separator or len(label) > 24 or not remainder.strip():
        return [(None, line) for line in _wrap(text, width - 4, regular, size)]

    label = f"{label}:"
    first_width = width - 24 - bold.text_length(label, fontsize=size) - regular.text_length(" ", fontsize=size)
    body_lines = _wrap(remainder.strip(), first_width, regular, size)
    if not body_lines:
        return [(label, "")]
    return [(label, body_lines[0])] + [(None, line) for line in _wrap(
        " ".join(remainder.strip().split()[len(body_lines[0].split()):]), width - 4, regular, size
    )]


def _draw_paragraph(page, text, x, y, width, regular, bold, size, line_height, color):
    lines = _paragraph_lines(text, width, regular, bold, size)
    for label, body in lines:
        if label:
            page.insert_text((x, y), label, fontsize=size, fontname="hebo", color=color)
            label_width = bold.text_length(label, fontsize=size)
            page.insert_text((x + label_width + regular.text_length(" ", fontsize=size), y),
                             body, fontsize=size, fontname="helv", color=color)
        else:
            page.insert_text((x, y), body, fontsize=size, fontname="helv", color=color)
        y += line_height
    return y


def _group_sections(content):
    sections = [section.strip() for section in content.split("\n\n") if section.strip()]
    groups = []
    for section in sections:
        heading = section.splitlines()[0].strip()
        question = re.match(r"^\d+\.", heading) or re.match(r"^\d+\s+Constructed Response", heading)
        boundary = re.match(r"^Passage \d+\b", heading) or heading == "Final Compact Key"
        if question or boundary:
            groups.append([section])
        elif groups and (
            re.match(r"^\d+\.", groups[-1][0].splitlines()[0].strip())
            or re.match(r"^\d+\s+Constructed Response", groups[-1][0].splitlines()[0].strip())
            or groups[-1][0].splitlines()[0].strip() == "Final Compact Key"
        ):
            groups[-1].append(section)
        else:
            groups.append([section])
    return groups


def render_ela_teacher(manifest, destination):
    import pymupdf

    pages = manifest["pages"]
    if len(pages) != 2:
        raise ValueError("The historical ELA teacher profile requires two pages")
    answers = re.findall(r"Correct Answer:\s*([A-D])", "\n".join(pages))
    if answers != manifest["official_answers"] or len(answers) != 12:
        raise ValueError("YPQA answers must match the twelve recorded official answers")

    regular = pymupdf.Font("helv")
    bold = pymupdf.Font("hebo")
    navy = (0.12, 0.22, 0.35)
    gray = (0.96, 0.97, 0.98)
    with pymupdf.open() as output:
        for page_number, content in enumerate(pages, 1):
            page = output.new_page(width=612, height=792)
            sections = _group_sections(content)
            y = 44
            if page_number == 1:
                page.insert_text((171, y), "MTS ELA MOCK TEST", fontsize=16, fontname="hebo", color=navy)
                y += 20
                if sections and sections[0][0] == "MTS ELA MOCK TEST":
                    sections.pop(0)
                subtitle = ""
                if sections and sections[0][0].startswith("Grade 6"):
                    subtitle = sections.pop(0)[0].replace("\n", " ")
                if subtitle:
                    subtitle = subtitle.translate(_PUNCTUATION)
                    subtitle_width = regular.text_length(subtitle, fontsize=9.5)
                    page.insert_text(((612 - subtitle_width) / 2, y), subtitle,
                                     fontsize=9.5, fontname="hebo", color=navy)
                    y += 20

            for section_group in sections:
                lines = [
                    line.strip().translate(_PUNCTUATION)
                    for section in section_group
                    for line in section.splitlines()
                    if line.strip()
                ]
                if not lines:
                    continue
                heading = lines[0]
                body = lines[1:]
                if re.match(r"^Passage \d+\b", heading) or heading == "Final Compact Key":
                    size = 11 if heading.startswith("Passage ") else 10
                    y += 3
                    page.insert_text((40, y + size), heading, fontsize=size, fontname="hebo", color=navy)
                    y += size + 8
                    for paragraph in body:
                        y = _draw_paragraph(page, paragraph, 40, y, 532, regular, bold,
                                            8.2, 9.5, (0, 0, 0))
                        y += 2
                    y += 2
                    continue

                if re.match(r"^\d+\.", heading) or re.match(r"^\d+\s+Constructed Response", heading):
                    size = 8.2
                    line_groups = [
                        _paragraph_lines(paragraph, 516, regular, bold, size)
                        for paragraph in body
                    ]
                    card_height = 22 + sum(len(group) * 9.5 for group in line_groups)
                    card_height += max(0, len(body) - 1) * 2 + 5
                    page.draw_rect(pymupdf.Rect(40, y, 572, y + card_height),
                                   color=None, fill=gray, overlay=True)
                    page.insert_text((46, y + 12), heading, fontsize=9, fontname="hebo", color=navy)
                    paragraph_y = y + 25
                    for paragraph, wrapped in zip(body, line_groups):
                        for label, text in wrapped:
                            if label:
                                page.insert_text((46, paragraph_y), label, fontsize=size,
                                                 fontname="hebo", color=navy)
                                label_width = bold.text_length(label, fontsize=size)
                                page.insert_text((46 + label_width + regular.text_length(" ", fontsize=size),
                                                  paragraph_y), text, fontsize=size, fontname="helv")
                            else:
                                page.insert_text((46, paragraph_y), text, fontsize=size, fontname="helv")
                            paragraph_y += 9.5
                        paragraph_y += 2
                    y += card_height + 4
                    continue

                y = _draw_paragraph(page, heading, 40, y, 532, regular, bold,
                                    8.2, 9.5, (0, 0, 0))
                for paragraph in body:
                    y = _draw_paragraph(page, paragraph, 40, y, 532, regular, bold,
                                        8.2, 9.5, (0, 0, 0))
                y += 3

            if y > 756:
                raise ValueError(
                    f"ELA teacher page {page_number} content ends at {y:.1f} pt, beyond the 756 pt limit"
                )
            footer = f"MTS ELA Mock Test | Grade 6 | {page_number}"
            footer_width = regular.text_length(footer, fontsize=8)
            page.insert_text(((612 - footer_width) / 2, 773), footer,
                             fontsize=8, fontname="helv", color=navy)
        output.save(destination, garbage=4, deflate=True)
