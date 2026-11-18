"""Render the recovered two-page ELA YPQA teacher content for local review."""
import re


def render_ela_teacher(manifest, destination):
    import pymupdf

    pages = manifest["pages"]
    if len(pages) != 2:
        raise ValueError("The historical ELA teacher profile requires two pages")
    answers = re.findall(r"Correct Answer:\s*([A-D])", "\n".join(pages))
    if answers != manifest["official_answers"] or len(answers) != 12:
        raise ValueError("YPQA answers must match the twelve recorded official answers")
    font = pymupdf.Font("helv")
    with pymupdf.open() as output:
        for content in pages:
            page = output.new_page(width=612, height=792)
            page.insert_text((34, 32), manifest["title"], fontsize=12, fontname="hebo")
            y = 54
            for paragraph in content.splitlines():
                paragraph = paragraph.strip()
                if not paragraph:
                    y += 2
                    continue
                # Keep the original YPQA content in an independently typeset review layout.
                line = ""
                for word in paragraph.split():
                    candidate = f"{line} {word}".strip()
                    if line and font.text_length(candidate, fontsize=8.2) > 544:
                        page.insert_text((34, y), line, fontsize=8.2)
                        y += 9.5
                        line = word
                    else:
                        line = candidate
                if y > 750:
                    raise ValueError("ELA teacher content exceeds the two-page profile")
                page.insert_text((34, y), line, fontsize=8.2)
                y += 9.5
            if y > 760:
                raise ValueError("ELA teacher content exceeds the two-page profile")
        output.save(destination, garbage=4, deflate=True)