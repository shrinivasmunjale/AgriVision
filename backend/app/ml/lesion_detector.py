"""
Lesion / infected-spot localizer for leaf disease images.

Why this module exists
----------------------
The deployed YOLOv8 model (``best.pt``) was trained on PlantVillage-style leaf
images where a single leaf fills the frame, so its boxes span the *whole leaf*
(often 60-100% of the photo). Drawing those boxes on the frontend therefore
"covers the whole image" instead of showing the infected area.

This module finds the *actual* diseased spots inside the leaf region and returns
tight bounding boxes around only those spots. It is a pure computer-vision stage
(OpenCV + numpy) that runs after YOLO leaf detection:

    1. Restrict the analysis to the leaf ROI (the YOLO leaf box).
    2. Build a per-pixel "lesion mask" with colour heuristics in BGR/HSV space:
       - brown / dark necrotic spots      (early & late blight, septoria, ...)
       - yellow / chlorotic blotches      (yellow leaf curl, yellowing)
       - pale / white mildew areas        (leaf mold, powdery blight)
       - large distance from the dominant healthy-green colour (adaptive)
    3. Clean the mask with morphological open/close.
    4. Find connected blobs and emit one box per blob.
    5. Large blobs (dense clusters of spots that merged) are split into tighter
       sub-regions using a grid-density clustering step.

The output uses the exact box schema the rest of the app expects:
    {
        "box_2d":     [ymin, xmin, ymax, xmax]  # normalized 0..1
        "box_pixels": [xmin, ymin, xmax, ymax]  # original-image pixels
        "label":      str
        "confidence": float
        "disease_id": int | None
    }
"""

from typing import List, Dict, Optional

import cv2
import numpy as np
from PIL import Image


# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
MAX_ANALYSIS_DIM = 1400          # downscale larger images for speed
MIN_SPOT_AREA_RATIO = 0.0008     # ignore smaller specks (relative to ROI area)
MAX_BOXES = 8                    # cap on boxes returned to the frontend
SMALL_BOX_AREA_FRAC = 0.30       # blobs bigger than 30% of the search area get split
GRID_CELL_FRACTION = 0.035       # grid cells ~3.5% of the blob width/height
CELL_MIN_DENSITY = 0.04          # a grid cell is "lesion" if >=4% covered
FILL_SOLID_RATIO = 0.72          # blobs filled >=72% are kept whole (truly necrotic)


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #
def _prepare_frame(image: Image.Image):
    """Return (BGR float32 arrays, scale-to-original factor)."""
    frame = np.asarray(image.convert("RGB"))
    h, w = frame.shape[:2]
    scale = 1.0
    work = frame
    if max(h, w) > MAX_ANALYSIS_DIM:
        scale = MAX_ANALYSIS_DIM / float(max(h, w))
        work = cv2.resize(
            frame,
            (max(1, int(w * scale)), max(1, int(h * scale))),
            interpolation=cv2.INTER_AREA,
        )
    bgr = cv2.cvtColor(work, cv2.COLOR_RGB2BGR).astype(np.float32)
    return bgr, scale


def _map_roi(roi, x0, y0, x1, y1):
    """Project a full-frame ROI into the (possibly downscaled) work space."""
    if roi is None:
        return x0, y0, x1, y1
    rx0 = max(x0, int(roi[0]))
    ry0 = max(y0, int(roi[1]))
    rx1 = min(x1, int(roi[2]))
    ry1 = min(y1, int(roi[3]))
    if rx1 <= rx0:
        rx0, rx1 = x0, x1
    if ry1 <= ry0:
        ry0, ry1 = y0, y1
    return rx0, ry0, rx1, ry1


def _leaf_reference_color(bgr, x0, y0, x1, y1):
    """Dominant healthy-green colour inside the search region (robust median)."""
    r = bgr[y0:y1, x0:x1, 2].ravel()
    g = bgr[y0:y1, x0:x1, 1].ravel()
    b = bgr[y0:y1, x0:x1, 0].ravel()

    greenish = (g > 55) & (g > r * 0.85) & (g > b * 0.85)
    if int(greenish.sum()) >= 40:
        return (
            float(np.percentile(r[greenish], 50)),
            float(np.percentile(g[greenish], 50)),
            float(np.percentile(b[greenish], 50)),
        )

    bright = np.maximum(r, np.maximum(g, b)) > 55
    if bool(bright.any()):
        return (
            float(np.percentile(r[bright], 45)),
            float(np.percentile(g[bright], 45)),
            float(np.percentile(b[bright], 45)),
        )
    return 90.0, 130.0, 70.0


def _build_lesion_mask(bgr, ref_r, ref_g, ref_b, x0, y0, x1, y1):
    """Create the boolean lesion mask restricted to the search region."""
    h, w = bgr.shape[:2]

    b = bgr[..., 0]
    g = bgr[..., 1]
    r = bgr[..., 2]
    mean = (r + g + b) / 3.0
    maxc = np.maximum(r, np.maximum(g, b))
    minc = np.minimum(r, np.minimum(g, b))
    sat = np.where(maxc > 0, (maxc - minc) / np.maximum(maxc, 1e-6), 0) * 255.0
    val = maxc

    # HSV hue (OpenCV range 0..179): green ~60, yellow ~30, brown ~10-20
    mx = maxc
    mn = minc
    delta = mx - mn + 1e-6
    hue = np.zeros_like(mx)
    m = delta > 0
    rc = np.where(m, (((mx - r) / delta) % 6.0), 0.0)
    gc = np.where(m, ((mx - g) / delta) + 2.0, 0.0)
    bc = np.where(m, ((mx - b) / delta) + 4.0, 0.0)
    hue = np.where(m & (mx == r), bc, hue)
    hue = np.where(m & (mx == g), rc, hue)
    hue = np.where(m & (mx == b), gc, hue)
    hue = hue * 30.0

    # 1) brown / reddish necrosis
    brown = (r - g) > 10
    # 2) tan / desaturated necrotic spots (early & late blight, septoria) that
    #    are too pale for the "brown" rule (needs warm hue + saturation)
    tan = (r >= g) & (hue <= 40) & (hue >= 4) & (sat >= 15) & (sat <= 95) & (val >= 65) & (val <= 205)
    # 3) dark necrotic tissue (needs a little colour so black background corners are excluded)
    dark = (mean < 60) & (sat > 22)
    # 4) yellow / chlorotic blotches
    yellow = (np.abs(g - r) < 20) & ((g - b) > 28) & (val > 85)
    # 5) pale / white mildew areas (bright, low saturation - but NOT plain white background)
    pale = (mean > 185) & (sat >= 12) & (sat < 90) & (val > 130)

    lesion = brown | tan | dark | yellow | pale

    # 6) adaptive catch-all: *coloured* pixels far from the healthy-green reference
    if ref_g > 60:
        dist = np.sqrt((r - ref_r) ** 2 + (g - ref_g) ** 2 + (b - ref_b) ** 2)
        lesion |= (dist > 90) & (mean > 40) & (sat > 15)

    # 7) drop only plain backgrounds (pure white / near-black); gray leaf shades
    #    and desaturated necrosis are handled separately by the blob rim filter.
    bg = ((sat < 8) & (val > 200)) | (val < 25)
    lesion &= ~bg

    mask = (lesion * 255).astype(np.uint8)
    # restrict to the search region
    out = np.zeros((h, w), np.uint8)
    out[y0:y1, x0:x1] = mask[y0:y1, x0:x1]
    return out


def _clean_mask(mask):
    k = max(2, int(round(0.006 * float(max(mask.shape[:2])))))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask


def _contour_boxes(mask, work_area, scale, min_area_px, bgr, x0, y0, x1, y1):
    """Bounding boxes (in original-image pixels) of the cleaned blobs.

    Blobs that smear along the search-region border and are essentially gray
    (background rim) are discarded so corner backgrounds don't become boxes.
    """
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    maxc = np.maximum(bgr[..., 0], np.maximum(bgr[..., 1], bgr[..., 2]))
    minc = np.minimum(bgr[..., 0], np.minimum(bgr[..., 1], bgr[..., 2]))
    sat = np.where(maxc > 0, (maxc - minc) / np.maximum(maxc, 1e-6), 0) * 255.0
    val = maxc

    boxes = []
    for c in cnts:
        area = float(cv2.contourArea(c))
        if area < min_area_px:
            continue
        x, y, bw, bh = cv2.boundingRect(c)
        if bw * bh < min_area_px * 1.5:
            continue
        # ignore razor-thin slivers
        if (bw > bh and bh < 2) or (bh > bw and bw < 2):
            continue
        if bw * bh > 0.985 * work_area:
            continue

        # background rim: blob touches the ROI border and is gray/flat
        touches_border = (
            x <= x0 + 2 or y <= y0 + 2 or x + bw >= x1 - 2 or y + bh >= y1 - 2
        )
        if touches_border:
            frag = mask[y:y + bh, x:x + bw]
            pix_s = sat[y:y + bh, x:x + bw][frag > 0]
            pix_v = val[y:y + bh, x:x + bw][frag > 0]
            pix_b = bgr[y:y + bh, x:x + bw, 0][frag > 0]
            pix_g = bgr[y:y + bh, x:x + bw, 1][frag > 0]
            pix_r = bgr[y:y + bh, x:x + bw, 2][frag > 0]
            sat_mean = float(np.mean(pix_s)) if len(pix_s) else 255.0
            val_mean = float(np.mean(pix_v)) if len(pix_v) else 0.0
            spread = float(np.mean(np.maximum(pix_r, np.maximum(pix_g, pix_b)) - np.minimum(pix_r, np.minimum(pix_g, pix_b)))) if len(pix_r) else 40.0
            # Gray background rim: nearly achromatic, mid-brightness
            if sat_mean < 20 and val_mean > 35 and val_mean < 205 and spread < 25:
                continue

        boxes.append(
            [x / scale, y / scale, (x + bw) / scale, (y + bh) / scale]
        )
    return boxes


def _split_blob(mask, box, grid_w, grid_h):
    """Split a large blob into tighter sub-boxes via grid-density clustering."""
    x0, y0, x1, y1 = [int(v) for v in box]
    w = max(1, x1 - x0)
    hgt = max(1, y1 - y0)
    cols = max(2, min(40, w // max(1, grid_w)))
    rows = max(2, min(40, hgt // max(1, grid_h)))

    cell_w = w / float(cols)
    cell_h = hgt / float(rows)
    sub = mask[y0:y1, x0:x1]

    # density map over the grid
    density = np.zeros((rows, cols), np.float32)
    for yy in range(rows):
        cy0, cy1 = int(yy * cell_h), min(hgt, int((yy + 1) * cell_h))
        for xx in range(cols):
            cx0, cx1 = int(xx * cell_w), min(w, int((xx + 1) * cell_w))
            cell = sub[cy0:cy1, cx0:cx1]
            area = float((cy1 - cy0) * (cx1 - cx0))
            if area <= 0:
                continue
            density[yy, xx] = float(np.count_nonzero(cell > 0)) / area

    thr = max(CELL_MIN_DENSITY, 2.0 / max(1.0, cell_w * cell_h))
    dense = (density > thr).astype(np.uint8)
    if int(dense.sum()) == 0:
        return [[x0, y0, x1, y1]]

    n, labels, _, _ = cv2.connectedComponentsWithStats(dense, connectivity=4)
    out = []
    for lbl in range(1, n):
        ys, xs = np.nonzero(labels == lbl)
        if len(xs) == 0:
            continue
        sx0 = x0 + int(xs.min() * cell_w)
        sy0 = y0 + int(ys.min() * cell_h)
        sx1 = x0 + int((xs.max() + 1) * cell_w)
        sy1 = y0 + int((ys.max() + 1) * cell_h)
        out.append([sx0, sy0, sx1, sy1])
    return out or [[x0, y0, x1, y1]]


def _merge_boxes(boxes):
    """Greedily merge boxes that overlap substantially."""
    merged = []
    for bx in boxes:
        placed = False
        for m in merged:
            ix0 = max(bx[0], m[0])
            iy0 = max(bx[1], m[1])
            ix1 = min(bx[2], m[2])
            iy1 = min(bx[3], m[3])
            inter = max(0, ix1 - ix0) * max(0, iy1 - iy0)
            a1 = (bx[2] - bx[0]) * (bx[3] - bx[1])
            a2 = (m[2] - m[0]) * (m[3] - m[1])
            if inter / max(1e-6, min(a1, a2)) > 0.65:
                m[0] = min(m[0], bx[0])
                m[1] = min(m[1], bx[1])
                m[2] = max(m[2], bx[2])
                m[3] = max(m[3], bx[3])
                placed = True
                break
        if not placed:
            merged.append(list(bx))
    return merged


def _to_box_schema(boxes, width, height, label, confidence, disease_id):
    """Convert raw pixel boxes to the app's box schema in original-image coords."""
    out = []
    for bx in boxes:
        x0 = max(0.0, min(float(width), float(bx[0])))
        y0 = max(0.0, min(float(height), float(bx[1])))
        x1 = max(x0, min(float(width), float(bx[2])))
        y1 = max(y0, min(float(height), float(bx[3])))
        out.append(
            {
                "box_2d": [
                    round(y0 / height, 4),
                    round(x0 / width, 4),
                    round(y1 / height, 4),
                    round(x1 / width, 4),
                ],
                "box_pixels": [
                    round(x0, 1),
                    round(y0, 1),
                    round(x1, 1),
                    round(y1, 1),
                ],
                "label": label,
                "confidence": round(confidence, 4),
                "disease_id": disease_id,
            }
        )
    return out


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def localize_infected_regions(
    image: Image.Image,
    roi: Optional[List[float]] = None,
    label: str = "Infected Area",
    confidence: float = 0.0,
    disease_id: Optional[int] = None,
) -> List[Dict]:
    """
    Find tight boxes around the actual infected spots in ``image``.

    Args:
        image: RGB PIL image (original, full frame).
        roi:   Optional leaf region ``[xmin, ymin, xmax, ymax]`` in original
               image pixel coordinates. When given, the search is restricted to
               this region (recommended - pass the YOLO leaf box).
        label / confidence / disease_id: metadata attached to each returned box.

    Returns:
        List of box dicts (see module docstring). Empty list when no lesions
        can be localized.
    """
    try:
        width, height = image.size
        bgr, scale = _prepare_frame(image)
        h, w = bgr.shape[:2]

        # search region = ROI (or full frame); ROI is in original-image px so
        # scale it into the (possibly downscaled) work space first.
        scaled_roi = [v * scale for v in roi] if roi else None
        x0, y0, x1, y1 = _map_roi(scaled_roi, 0, 0, w, h)
        work_area = max(1, (x1 - x0) * (y1 - y0))

        ref_r, ref_g, ref_b = _leaf_reference_color(bgr, x0, y0, x1, y1)
        mask = _build_lesion_mask(bgr, ref_r, ref_g, ref_b, x0, y0, x1, y1)
        mask = _clean_mask(mask)

        min_area_px = max(16.0, MIN_SPOT_AREA_RATIO * work_area)
        boxes = _contour_boxes(mask, work_area, scale, min_area_px, bgr, x0, y0, x1, y1)

        # Iteratively split blobs that still cover too much of the search area.
        # A blob is only kept whole when it is (nearly) solid necrotic tissue.
        cells = list(boxes)
        max_whole_area = SMALL_BOX_AREA_FRAC * work_area * (scale * scale)
        for _ in range(6):
            best_fill = 1.0
            for bx in cells:
                x0i = int(round(bx[0] * scale))
                y0i = int(round(bx[1] * scale))
                x1i = int(round(bx[2] * scale))
                y1i = int(round(bx[3] * scale))
                area = (x1i - x0i) * (y1i - y0i)
                blob = mask[y0i:y1i, x0i:x1i]
                fill = float(np.count_nonzero(blob > 0)) / max(1.0, area)
                best_fill = min(best_fill, fill)
            if best_fill >= FILL_SOLID_RATIO:
                break
            split_boxes = []
            changed = False
            for bx in cells:
                x0i = int(round(bx[0] * scale))
                y0i = int(round(bx[1] * scale))
                x1i = int(round(bx[2] * scale))
                y1i = int(round(bx[3] * scale))
                area = (x1i - x0i) * (y1i - y0i)
                blob = mask[y0i:y1i, x0i:x1i]
                fill = float(np.count_nonzero(blob > 0)) / max(1.0, area)
                if area <= max_whole_area or fill >= FILL_SOLID_RATIO:
                    split_boxes.append(bx)
                    continue
                cell = max(8, int(GRID_CELL_FRACTION * (x1i - x0i)))
                cell_h = max(8, int(GRID_CELL_FRACTION * (y1i - y0i)))
                parts = _split_blob(mask, [x0i, y0i, x1i, y1i], cell, cell_h)
                if len(parts) == 1:
                    # split produced nothing smaller - keep original
                    split_boxes.append(bx)
                else:
                    changed = True
                    split_boxes.extend(parts)
            if not changed:
                break
            cells = split_boxes

        boxes = _merge_boxes(cells)

        # work-space coords -> original-image pixel coords
        pixel_boxes = [
            [bx[0] / scale, bx[1] / scale, bx[2] / scale, bx[3] / scale]
            for bx in boxes
        ]
        pixel_boxes = _merge_boxes(pixel_boxes)

        # sort biggest first, cap total
        pixel_boxes.sort(key=lambda b: (b[2] - b[0]) * (b[3] - b[1]), reverse=True)
        pixel_boxes = pixel_boxes[:MAX_BOXES]

        if not pixel_boxes:
            return []

        max_frac = (
            pixel_boxes[0][2] - pixel_boxes[0][0]
        ) * (pixel_boxes[0][3] - pixel_boxes[0][1]) / max(1, width * height)
        print(
            f"[LESION] Found {len(pixel_boxes)} infected region(s) "
            f"(max box covers {max_frac:.2f} of frame)"
        )
        return _to_box_schema(pixel_boxes, width, height, label, confidence, disease_id)
    except Exception as exc:  # pragma: no cover - never block inference
        print(f"[WARNING] Lesion localizer failed: {exc}")
        return []


def draw_boxes_debug(image: Image.Image, boxes: List[Dict], out_path: str = "lesion_debug.png"):
    """Debug helper: draw the boxes on the image and save a copy."""
    import PIL.ImageDraw

    dbg = image.convert("RGB")
    draw = PIL.ImageDraw.Draw(dbg)
    W, H = image.size
    for b in boxes:
        p = (b.get("box_pixels") or [])[:4]
        if not p:
            b2d = b.get("box_2d")
            if b2d:
                p = [b2d[1] * W, b2d[0] * H, b2d[3] * W, b2d[2] * H]
        if p:
            draw.rectangle(p, outline="red", width=max(2, int(W / 200)))
    dbg.save(out_path)
    print(f"[DEBUG] Saved annotated image to {out_path}")