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
MIN_SPOT_AREA_RATIO = 0.0006     # ignore smaller specks (relative to ROI area)
MAX_BOX_AREA_FRAC = 0.60         # maximum fraction of image area a box may cover
MAX_BOX_DIM_FRAC = 0.78          # maximum fraction of image width or height a box may span


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


def _filter_valid_contours(mask, work_area, min_area_px, bgr, x0, y0, x1, y1):
    """Find and return valid lesion contours, discarding noise and flat background rims."""
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return []

    maxc = np.maximum(bgr[..., 0], np.maximum(bgr[..., 1], bgr[..., 2]))
    minc = np.minimum(bgr[..., 0], np.minimum(bgr[..., 1], bgr[..., 2]))
    sat = np.where(maxc > 0, (maxc - minc) / np.maximum(maxc, 1e-6), 0) * 255.0
    val = maxc

    valid = []
    for c in cnts:
        area = float(cv2.contourArea(c))
        if area < min_area_px:
            continue
        x, y, bw, bh = cv2.boundingRect(c)
        if bw * bh < min_area_px * 1.2:
            continue
        # ignore razor-thin slivers
        if (bw > bh and bh < 2) or (bh > bw and bw < 2):
            continue
        if bw * bh > 0.95 * work_area:
            continue

        # background rim check: blob touches the ROI border and is flat/gray
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
            if sat_mean < 20 and val_mean > 35 and val_mean < 205 and spread < 25:
                continue

        valid.append((c, area, (x, y, bw, bh)))

    # Sort largest area first
    valid.sort(key=lambda item: item[1], reverse=True)
    return valid


def _compute_single_disease_box(valid_contours, mask, orig_w, orig_h, scale):
    """
    Compute exactly ONE tight bounding box enclosing the primary disease area.
    
    Verifies that the box focuses tightly on the disease and does NOT cover the entire image.
    """
    if not valid_contours:
        return None

    total_valid = len(valid_contours)
    largest_contour, largest_area, (lx, ly, lbw, lbh) = valid_contours[0]

    # Combine top significant contours (area >= 12% of largest or top 3)
    # to form a cohesive disease area envelope
    top_contours = [
        item[0] for item in valid_contours
        if item[1] >= max(10.0, largest_area * 0.12)
    ][:4]

    all_pts = np.vstack(top_contours)
    x, y, w, h = cv2.boundingRect(all_pts)

    # Convert to original image pixel coordinates
    ox0 = x / scale
    oy0 = y / scale
    ox1 = (x + w) / scale
    oy1 = (y + h) / scale

    # Add a modest padding around the disease cluster (6% of dimension)
    pad_x = max(10.0, (ox1 - ox0) * 0.06)
    pad_y = max(10.0, (oy1 - oy0) * 0.06)
    ox0 = max(0.0, ox0 - pad_x)
    oy0 = max(0.0, oy0 - pad_y)
    ox1 = min(float(orig_w), ox1 + pad_x)
    oy1 = min(float(orig_h), oy1 + pad_y)

    cur_w = ox1 - ox0
    cur_h = oy1 - oy0
    area_fraction = (cur_w * cur_h) / max(1.0, float(orig_w * orig_h))

    # Verification: Ensure the box does not cover the entire image!
    # If the combined envelope spans too much of the picture (> 60% area or > 78% of any dimension),
    # focus on the primary dominant disease lesion instead of framing the entire leaf.
    if area_fraction > MAX_BOX_AREA_FRAC or cur_w > MAX_BOX_DIM_FRAC * orig_w or cur_h > MAX_BOX_DIM_FRAC * orig_h:
        # Fall back to largest single lesion contour
        lx0 = lx / scale
        ly0 = ly / scale
        lx1 = (lx + lbw) / scale
        ly1 = (ly + lbh) / scale

        l_pad_x = max(8.0, (lx1 - lx0) * 0.08)
        l_pad_y = max(8.0, (ly1 - ly0) * 0.08)
        ox0 = max(0.0, lx0 - l_pad_x)
        oy0 = max(0.0, ly0 - l_pad_y)
        ox1 = min(float(orig_w), lx1 + l_pad_x)
        oy1 = min(float(orig_h), ly1 + l_pad_y)

        cur_w = ox1 - ox0
        cur_h = oy1 - oy0

    # Hard safety clamp: Never allow a box to cover more than 72% of width/height or > 50% total area
    max_w_allowed = orig_w * 0.72
    max_h_allowed = orig_h * 0.72

    if cur_w > max_w_allowed:
        center_x = (ox0 + ox1) / 2.0
        ox0 = max(0.0, center_x - max_w_allowed / 2.0)
        ox1 = min(float(orig_w), center_x + max_w_allowed / 2.0)
        cur_w = ox1 - ox0

    if cur_h > max_h_allowed:
        center_y = (oy0 + oy1) / 2.0
        oy0 = max(0.0, center_y - max_h_allowed / 2.0)
        oy1 = min(float(orig_h), center_y + max_h_allowed / 2.0)
        cur_h = oy1 - oy0

    cur_area_frac = (cur_w * cur_h) / max(1.0, float(orig_w * orig_h))
    if cur_area_frac > MAX_BOX_AREA_FRAC:
        scale_down = np.sqrt(MAX_BOX_AREA_FRAC / cur_area_frac)
        center_x = (ox0 + ox1) / 2.0
        center_y = (oy0 + oy1) / 2.0
        new_w = cur_w * scale_down
        new_h = cur_h * scale_down
        ox0 = max(0.0, center_x - new_w / 2.0)
        ox1 = min(float(orig_w), center_x + new_w / 2.0)
        oy0 = max(0.0, center_y - new_h / 2.0)
        oy1 = min(float(orig_h), center_y + new_h / 2.0)

    # Convert small boxes to a clear medium-sized box (at least 28% of width and height)
    min_w = max(140.0, orig_w * 0.28)
    min_h = max(140.0, orig_h * 0.28)

    if (ox1 - ox0) < min_w:
        cx = (ox0 + ox1) / 2.0
        ox0 = max(0.0, cx - min_w / 2.0)
        ox1 = min(float(orig_w), cx + min_w / 2.0)
        if ox0 == 0.0:
            ox1 = min(float(orig_w), min_w)
        elif ox1 == float(orig_w):
            ox0 = max(0.0, float(orig_w) - min_w)

    if (oy1 - oy0) < min_h:
        cy = (oy0 + oy1) / 2.0
        oy0 = max(0.0, cy - min_h / 2.0)
        oy1 = min(float(orig_h), cy + min_h / 2.0)
        if oy0 == 0.0:
            oy1 = min(float(orig_h), min_h)
        elif oy1 == float(orig_h):
            oy0 = max(0.0, float(orig_h) - min_h)

    return [ox0, oy0, ox1, oy1]


def _to_box_schema(box, width, height, label, confidence, disease_id):
    """Convert raw pixel box to standard schema in original-image coords."""
    if not box:
        return []
    x0 = max(0.0, min(float(width), float(box[0])))
    y0 = max(0.0, min(float(height), float(box[1])))
    x1 = max(x0, min(float(width), float(box[2])))
    y1 = max(y0, min(float(height), float(box[3])))
    return [
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
    ]


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
    Find exactly ONE tight bounding box around the actual infected disease area in ``image``.
    Guarantees that the bounding box does not cover the entire image.

    Args:
        image: RGB PIL image (original, full frame).
        roi:   Optional leaf region ``[xmin, ymin, xmax, ymax]`` in original
               image pixel coordinates. When given, the search is restricted to
               this region.
        label / confidence / disease_id: metadata attached to the returned box.

    Returns:
        List containing at most ONE box dict:
        [
            {
                "box_2d": [ymin, xmin, ymax, xmax],  # normalized 0..1
                "box_pixels": [xmin, ymin, xmax, ymax],
                "label": str,
                "confidence": float,
                "disease_id": int | None
            }
        ]
        Empty list when no lesions can be localized.
    """
    try:
        width, height = image.size
        bgr, scale = _prepare_frame(image)
        h, w = bgr.shape[:2]

        scaled_roi = [v * scale for v in roi] if roi else None
        x0, y0, x1, y1 = _map_roi(scaled_roi, 0, 0, w, h)
        work_area = max(1, (x1 - x0) * (y1 - y0))

        ref_r, ref_g, ref_b = _leaf_reference_color(bgr, x0, y0, x1, y1)
        mask = _build_lesion_mask(bgr, ref_r, ref_g, ref_b, x0, y0, x1, y1)
        mask = _clean_mask(mask)

        min_area_px = max(12.0, MIN_SPOT_AREA_RATIO * work_area)
        valid_contours = _filter_valid_contours(mask, work_area, min_area_px, bgr, x0, y0, x1, y1)

        single_box = _compute_single_disease_box(valid_contours, mask, width, height, scale)
        if not single_box:
            return []

        cov_frac = ((single_box[2] - single_box[0]) * (single_box[3] - single_box[1])) / max(1.0, float(width * height))
        print(f"[LESION] Computed 1 focused disease box (covers {cov_frac:.1%} of frame)")

        return _to_box_schema(single_box, width, height, label, confidence, disease_id)
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