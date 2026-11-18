"""Extract official text and combine it with reviewed transcriptions of raster source pages."""

from hashlib import sha256
import json
from pathlib import Path
import re
import unicodedata
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "work/golden/NY_ELA_Grade6_2025_Released_Test_Questions.pdf"
if not SOURCE.exists():
    SOURCE = ROOT.parent / "golden/NY_ELA_Grade6_2025_Released_Test_Questions.pdf"


def clean(text):
    text = unicodedata.normalize(
        "NFKC", text.replace("\ue062", "Th").replace("\ue09d", "ft")
    )
    return " ".join(
        text.translate(
            str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'", "—": "-", "–": "-"})
        ).split()
    )


RASTER = {
    "purple": {
        8: "Here is how the Purple code and other Japanese diplomatic codes worked. The Japanese encoded a message using a special device called a cipher machine. Then they radioed the message forward. A U.S. radio station intercepted the message and sent it to Washington. There, the cryptanalysts went to work. When they had cracked the entire code, they built a machine just like the Japanese cipher machine and used it to decode other messages. Finally, translators turned these messages into English.",
        9: "A coded message consisted of a pattern of numbers and letters. It might look something like this: 78232 RSECO. Each symbol stood for a letter, but the letter it stood for changed as the machine moved forward. Each time this happened, a symbol would come to stand for something different, which made the code incredibly difficult to solve.",
        10: 'The cryptanalysts had to do a lot of guessing and checking their guesses. For example, they knew that many Japanese diplomatic messages began with the Japanese words "I have the honor to inform Your Excellency," so they tried that combination of letters first.',
    },
    "legacies": {
        6: "There are more than 500 varieties of lilacs and more than 1,200 lilac bushes at Highland Park. In 1888, the world's largest nursery, Ellwanger & Barry, owned by George Ellwanger and Patrick Barry, gave Highland Park to the people of Rochester. It was beautifully landscaped with trees and shrubs and was the first municipal arboretum in the United States. An arboretum is a place where trees, shrubs, and plants are specially grown and cultivated. The park's collection of lilacs originally started with 20 varieties in 1892. Since 1898, Rochester has held a Lilac Festival every May. The first event attracted 3,000 visitors; now more than 500,000 people come to see the lilacs and other flowering trees and shrubs. . . .",
        7: "You may think that lighthouses are interesting to look at, and they are. But they also serve a very useful purpose.",
        8: "Lighthouses guide ships sailing near a coast. They are built in different kinds of places: important locations on a coast, harbor entrances, islands, rocky ledges or reefs, and even in the water. They project strong beacons of light at night so ships can see them. Lighthouses help ships identify their locations, warn them of danger, and serve as a marker of nearby land.",
        9: "The Montauk Point Lighthouse on Long Island, New York, is more than 200 years old. Built in 1796, it is the oldest lighthouse in the state. It has guided whaling ships, fishing boats, steamships, submarines, and sailboats for many years and continues to do so today. The tower is more than 110 feet tall, and a person has to climb 137 steps to get to the top. But the Montauk Point Lighthouse is not just a tower. Attached to it is a house in which the lighthouse keeper lived with his family and assistants. Since the light on top of the tower was automated in 1987, the lighthouse no longer needs a keeper. . . .",
        10: "From the 1850s through the early 1900s, thousands of immigrants arrived in the United States and lived in New York City. They came from Ireland and Germany and, later, from Italy, Eastern Europe, and China, among other places. Because most immigrants were poor when they arrived, they often lived on the Lower East Side of Manhattan, where rents for the crowded apartment buildings, called tenements, were low.",
    },
}


def paragraphs(page, numbers):
    blocks = page.get_text("blocks")
    result = {}
    for num in numbers:
        anchor = next(
            b
            for b in blocks
            if b[0] < 100
            and (
                b[4].strip() == str(num) or re.search(r"\n" + str(num) + r"\s*$", b[4])
            )
        )
        if len(anchor[4].strip()) > 3:
            text = re.sub(r"\n" + str(num) + r"\s*$", "", anchor[4])
        else:
            text = next(
                b[4] for b in blocks if b[0] > 100 and abs(b[1] - anchor[1]) < 2
            )
        result[num] = clean(text)
    return result


def questions(doc, pages):
    result = []
    for number in pages:
        blocks = doc[number - 1].get_text("blocks")
        anchors = sorted(
            (b[1] - 12, int(b[4].strip()))
            for b in blocks
            if b[0] < 72 and b[4].strip().isdigit()
        )
        for idx, (start, num) in enumerate(anchors):
            end = anchors[idx + 1][0] if idx + 1 < len(anchors) else 690
            text = []
            for b in sorted(
                (b for b in blocks if b[0] >= 70 and start <= b[1] < end),
                key=lambda b: (b[1], b[0]),
            ):
                value = clean(b[4])
                if re.fullmatch("[A-D]", value) and text:
                    text.append(value + ". " + text.pop())
                else:
                    text.append(value)
            result.append({"source_number": num, "blocks": text, "source_page": number})
    return result


with pymupdf.open(SOURCE) as doc:
    purple = (
        paragraphs(doc[8], range(1, 8))
        | RASTER["purple"]
        | paragraphs(doc[10], [11, 12])
    )
    legacies = (
        paragraphs(doc[14], range(1, 6))
        | RASTER["legacies"]
        | paragraphs(doc[16], [11])
    )
    qs = questions(doc, [12, 13, 14, 18, 19, 20, 21])
    assert [r["source_number"] for r in qs] == [*range(8, 15), *range(22, 29)]
    for i, q in enumerate(qs, 1):
        q["output_number"] = i
    manifest = {
        "profile": "ela_grade6_ny2025",
        "source_sha256": sha256(SOURCE.read_bytes()).hexdigest(),
        "raster_transcription_source_pages": [10, 16],
        "passages": [
            {
                "title": "Cracking Code Purple",
                "author": "Anna Ouchchy",
                "paragraphs": purple,
                "headings": {
                    "4": "The Purple Solution",
                    "8": "How the System Worked",
                    "11": "Making Magic",
                },
                "split_before": 8,
            },
            {
                "title": "Excerpt from New York: Local Legacies",
                "author": "Library of Congress",
                "paragraphs": legacies,
                "context": clean(
                    next(b[4] for b in doc[14].get_text("blocks") if 110 < b[1] < 113)
                ),
                "headings": {
                    "1": "One-Room Schoolhouse: A Local Legacy",
                    "5": "Rochester, New York's Lilac Festival: A Local Legacy",
                    "7": "Montauk Point Lighthouse Museum: A Local Legacy",
                    "10": "Immigrant Life in New York: A Local Legacy",
                },
                "split_before": 7,
            },
        ],
        "questions": qs,
        "cipher": {"source_page": 10, "bounds": [162, 293, 452, 562]},
        "verification": "Source-derived text, with manually transcribed raster pages. Full fidelity review pending.",
    }
    dest = ROOT / "specs/generate_mock_assessment/fixtures/ela-student-manifest.json"
    dest.write_bytes((json.dumps(manifest, indent=2) + "\n").encode())
    print("Extracted 23 passage paragraphs and 14 questions; no golden PDF input.")
