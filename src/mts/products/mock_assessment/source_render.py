"""Compose a local review PDF from explicit, revision-bound source crops."""
from hashlib import sha256
import math
from pathlib import Path


def render_student(source_path, manifest, destination, *, rasterize_crops=False):
    """Pack atomic crops on Letter pages and return their placements."""
    import pymupdf

    source_path = Path(source_path)
    source_bytes = source_path.read_bytes()
    if sha256(source_bytes).hexdigest() != manifest["source_sha256"]:
        raise ValueError("Source PDF hash does not match the region manifest")

    regions = manifest["regions"]
    ids = [region["id"] for region in regions]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError("Region IDs must be nonempty and unique")

    scale = manifest["scale"]
    if not math.isfinite(scale) or not 0.70 <= scale <= 1:
        raise ValueError("Crop scale must be between 70% and 100%")
    page_limit = manifest.get("maximum_pages")
    if page_limit is not None and (type(page_limit) is not int or page_limit < 1):
        raise ValueError("Maximum pages must be a positive integer")

    placements = []
    with pymupdf.open(stream=source_bytes, filetype="pdf") as original, pymupdf.open() as output:
        column = 1
        cursor = 756
        left_bottom = column_top = 64
        for region in regions:
            number = region["source_page"]
            if type(number) is not int or not 1 <= number <= len(original):
                raise ValueError(f"Invalid source page for region {region['id']}")
            clips = []
            for coordinates in region.get("parts", [region.get("bounds")]):
                if not coordinates or len(coordinates) != 4 or not all(math.isfinite(v) for v in coordinates):
                    raise ValueError(f"Invalid bounds for region {region['id']}")
                clip = pymupdf.Rect(coordinates)
                if clip.is_empty or not original[number - 1].rect.contains(clip):
                    raise ValueError(f"Crop is empty or outside source page for region {region['id']}")
                clips.append(clip)
            gap = region.get("part_gap_pt", 8)
            if not clips or not math.isfinite(gap) or gap < 0:
                raise ValueError(f"Invalid component layout for region {region['id']}")
            width = max(clip.width for clip in clips) * scale
            height = sum(clip.height for clip in clips) * scale + gap * (len(clips) - 1)
            if width > 540 or height > 692:
                raise ValueError(f"Atomic region {region['id']} does not fit on Letter")
            compact = width <= 262
            if compact and column == 0 and cursor + height > 756:
                left_bottom = cursor
                column = 1
                cursor = column_top
            if not compact and column == 1:
                cursor = max(cursor, left_bottom)
            if cursor + height > 756:
                if page_limit is not None and len(output) >= page_limit:
                    raise ValueError(f"Page ceiling of {page_limit} exceeded")
                page = output.new_page(width=612, height=792)
                page.insert_text((36, 36), manifest["title"], fontsize=12)
                page.insert_text((550, 773), str(len(output)), fontsize=9)
                column = 0
                cursor = 64
                left_bottom = column_top = 64
            x = 314 if compact and column == 1 else 36
            target = pymupdf.Rect(x, cursor, x + width, cursor + height)
            part_y = cursor
            for clip in clips:
                part = pymupdf.Rect(x, part_y, x + clip.width * scale, part_y + clip.height * scale)
                if rasterize_crops:
                    # A clipped vector form still embeds the original page contents.
                    pixel_clip = pymupdf.Rect(
                        math.ceil(clip.x0 * 4) / 4, math.ceil(clip.y0 * 4) / 4,
                        math.floor(clip.x1 * 4) / 4, math.floor(clip.y1 * 4) / 4,
                    )
                    if pixel_clip.is_empty:
                        raise ValueError(f"Crop is too small to rasterize for region {region['id']}")
                    pixels = original[number - 1].get_pixmap(dpi=288, clip=pixel_clip, annots=False)
                    pixel_target = pymupdf.Rect(
                        part.x0 + (pixel_clip.x0 - clip.x0) * scale,
                        part.y0 + (pixel_clip.y0 - clip.y0) * scale,
                        part.x0 + (pixel_clip.x1 - clip.x0) * scale,
                        part.y0 + (pixel_clip.y1 - clip.y0) * scale,
                    )
                    page.insert_image(pixel_target, pixmap=pixels, keep_proportion=False)
                else:
                    page.show_pdf_page(part, original, number - 1, clip=clip)
                part_y = part.y1 + gap
            placements.append({
                "id": region["id"], "page": len(output), "bounds": list(target), "scale": scale
            })
            cursor = target.y1 + 8
            if not compact:
                column = 0
                left_bottom = column_top = cursor
        output.save(destination, garbage=4, deflate=True)
    return placements



