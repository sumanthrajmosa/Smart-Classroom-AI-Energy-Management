"""Image, calibrated zone and OpenCV body-region utilities for Approach B."""
import os
import cv2
import numpy as np
from config import (
    CAMERA_ZONE_PROFILES, DEFAULT_CAMERA_PROFILE, REGION_COLORS,
    BODY_WIDTH_FACE_MULTIPLIER, BODY_HEIGHT_FACE_MULTIPLIER,
    BODY_TOP_FACE_MULTIPLIER,
)

ZONE_ORDER = ("BACK_LEFT", "BACK_RIGHT", "FRONT_LEFT", "FRONT_RIGHT")


def load_image(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    image = cv2.imread(path)
    if image is None:
        raise ValueError(f"Cannot read image: {path}")
    return image


def save_image(path, image):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    if not cv2.imwrite(path, image):
        raise IOError(f"Could not save {path}")


def _interp_profile(points, value):
    """Linear interpolation over normalized calibration points."""
    points = sorted((float(a), float(b)) for a, b in points)
    if value <= points[0][0]:
        return points[0][1]
    if value >= points[-1][0]:
        return points[-1][1]
    for (a0, b0), (a1, b1) in zip(points[:-1], points[1:]):
        if a0 <= value <= a1:
            t = (value - a0) / max(1e-9, a1 - a0)
            return b0 + t * (b1 - b0)
    return points[-1][1]


def _split_x_at_y(profile, y_norm):
    if "split_x_points" in profile:
        return _interp_profile(profile["split_x_points"], y_norm)
    return float(profile.get("split_x", 0.5))


def _split_y_at_x(profile, x_norm):
    if "split_y_points" in profile:
        return _interp_profile(profile["split_y_points"], x_norm)
    return float(profile.get("split_y", 0.5))


def get_polygons(width, height, profile_name=None):
    """Build four perspective-aware polygons covering the entire image."""
    profile_name = profile_name or DEFAULT_CAMERA_PROFILE
    profile = CAMERA_ZONE_PROFILES.get(
        profile_name, CAMERA_ZONE_PROFILES[DEFAULT_CAMERA_PROFILE]
    )
    # Sample boundaries densely to render smooth perspective-following edges.
    xs = np.linspace(0, width - 1, 80)
    ys = np.linspace(0, height - 1, 80)

    horizontal = np.asarray([
        (int(round(x)), int(round(_split_y_at_x(profile, x / max(1, width - 1)) * (height - 1))))
        for x in xs
    ], dtype=np.int32)

    vertical = np.asarray([
        (int(round(_split_x_at_y(profile, y / max(1, height - 1)) * (width - 1))), int(round(y)))
        for y in ys
    ], dtype=np.int32)

    # The four polygons are formed by the image border and the two calibrated
    # boundaries. They tile the complete image, including the aisle, so every
    # face center is always inside exactly one zone.
    top_left = [(0, 0)] + [tuple(p) for p in vertical if p[1] <= horizontal[0][1]] + [tuple(horizontal[0])]
    # For robust geometry and consistent membership, construct zones by
    # evaluating the two split functions at each point rather than relying on
    # rasterized polygon edge inclusion.
    return {
        "_profile": profile,
        "_width": width,
        "_height": height,
        "_horizontal": horizontal,
        "_vertical": vertical,
    }


def point_region(point, polygons):
    """Assign by face-level coordinate against calibrated view boundaries."""
    x, y = float(point[0]), float(point[1])
    width, height = polygons["_width"], polygons["_height"]
    profile = polygons["_profile"]
    xn = min(1.0, max(0.0, x / max(1, width - 1)))
    yn = min(1.0, max(0.0, y / max(1, height - 1)))
    split_x = _split_x_at_y(profile, yn)
    split_y = _split_y_at_x(profile, xn)
    is_left = xn < split_x
    is_back = yn < split_y
    if is_back:
        return "BACK_LEFT" if is_left else "BACK_RIGHT"
    return "FRONT_LEFT" if is_left else "FRONT_RIGHT"


def _zone_masks(polygons):
    """Vectorized masks for the four calibrated zones (fast for batch runs)."""
    width, height = polygons["_width"], polygons["_height"]
    profile = polygons["_profile"]
    yy, xx = np.indices((height, width), dtype=np.float32)
    xn = xx / max(1, width - 1)
    yn = yy / max(1, height - 1)

    if "split_x_points" in profile:
        xp = np.asarray(profile["split_x_points"], dtype=np.float32)
        split_x = np.interp(yn[:, 0], xp[:, 0], xp[:, 1])[:, None]
        split_x = np.broadcast_to(split_x, (height, width))
    else:
        split_x = np.full((height, width), float(profile.get("split_x", 0.5)), np.float32)

    if "split_y_points" in profile:
        yp = np.asarray(profile["split_y_points"], dtype=np.float32)
        split_y = np.interp(xn[0, :], yp[:, 0], yp[:, 1])[None, :]
        split_y = np.broadcast_to(split_y, (height, width))
    else:
        split_y = np.full((height, width), float(profile.get("split_y", 0.5)), np.float32)

    left = xn < split_x
    back = yn < split_y
    return {
        "BACK_LEFT": back & left,
        "BACK_RIGHT": back & ~left,
        "FRONT_LEFT": ~back & left,
        "FRONT_RIGHT": ~back & ~left,
    }


def _draw_zone_overlay(image, polygons, counts, method_label, profile_name):
    out = image.copy()
    overlay = out.copy()
    height, width = out.shape[:2]
    # Fill using the same calibrated functions used for face assignment.
    zones = _zone_masks(polygons)
    for name in ZONE_ORDER:
        overlay[zones[name]] = REGION_COLORS[name]
    out = cv2.addWeighted(overlay, 0.10, out, 0.90, 0)

    # Draw calibrated vertical and horizontal boundary lines.
    cv2.polylines(out, [polygons["_vertical"]], False, (0, 255, 255), 3, cv2.LINE_AA)
    cv2.polylines(out, [polygons["_horizontal"]], False, (0, 255, 255), 3, cv2.LINE_AA)

    label_positions = {
        "BACK_LEFT": (12, 30), "BACK_RIGHT": (width - 245, 30),
        "FRONT_LEFT": (12, height - 20), "FRONT_RIGHT": (width - 245, height - 20),
    }
    for name in ZONE_ORDER:
        x, y = label_positions[name]
        cv2.putText(out, f"{name}: {counts.get(name, 0)}", (max(8, x), max(22, y)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.62, REGION_COLORS[name], 2, cv2.LINE_AA)

    total = sum(counts.values())
    cv2.rectangle(out, (8, 42), (min(width - 8, 640), 88), (20, 20, 20), -1)
    cv2.putText(out, f"{method_label}: {total}", (18, 72),
                cv2.FONT_HERSHEY_SIMPLEX, 0.68, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(out, f"{profile_name} | Unassigned: 0", (18, height - 48),
                cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def _grabcut_body_anchor(image, face_bbox):
    """Estimate torso anchor with classical OpenCV GrabCut."""
    x1, y1, x2, y2 = map(int, face_bbox)
    height, width = image.shape[:2]
    fw, fh = max(1, x2 - x1), max(1, y2 - y1)
    cx = (x1 + x2) // 2
    rx = max(10, int(1.8 * fw))
    top = max(0, int(y1 + 0.35 * fh))
    bottom = min(height, int(y2 + 4.4 * fh))
    left, right = max(0, cx - rx), min(width, cx + rx)
    if right - left < 12 or bottom - top < 18:
        return None, None
    roi = image[top:bottom, left:right].copy()
    rh, rw = roi.shape[:2]
    if rw < 12 or rh < 18:
        return None, None
    mask = np.full((rh, rw), cv2.GC_PR_BGD, np.uint8)
    mx, my = max(2, int(0.08 * rw)), max(2, int(0.04 * rh))
    mask[my:rh-my, mx:rw-mx] = cv2.GC_PR_FGD
    fx1, fx2 = max(0, x1-left), min(rw, x2-left)
    fy1, fy2 = max(0, y1-top), min(rh, y2-top)
    if fx2 > fx1 and fy2 > fy1:
        mask[fy1:fy2, fx1:fx2] = cv2.GC_FGD
    bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    try:
        cv2.grabCut(roi, mask, None, bgd, fgd, 3, cv2.GC_INIT_WITH_MASK)
    except cv2.error:
        return None, None
    foreground = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    torso_start = min(rh - 1, max(0, int((y2-top) + 0.25 * fh)))
    torso = foreground[torso_start:, :]
    if torso.size == 0:
        return None, None
    n, labels, component_stats, centroids = cv2.connectedComponentsWithStats((torso > 0).astype(np.uint8), 8)
    if n <= 1:
        return None, None
    component = 1 + int(np.argmax(component_stats[1:, cv2.CC_STAT_AREA]))
    area = int(component_stats[component, cv2.CC_STAT_AREA])
    if area < max(30, int(0.008 * rw * max(1, rh - torso_start))):
        return None, None
    local_cx, local_cy = centroids[component]
    anchor = (int(left + local_cx), int(top + torso_start + local_cy))
    bx, by, bw, bh, _ = component_stats[component]
    body_box = (left + int(bx), top + torso_start + int(by),
                left + int(bx + bw), top + torso_start + int(by + bh))
    return anchor, body_box


def _geometric_body_fallback(image_shape, face_bbox):
    height, width = image_shape[:2]
    x1, y1, x2, y2 = map(int, face_bbox)
    fw, fh = max(1, x2 - x1), max(1, y2 - y1)
    cx = (x1 + x2) // 2
    half = int((BODY_WIDTH_FACE_MULTIPLIER / 2.0) * fw)
    top = int(y1 + BODY_TOP_FACE_MULTIPLIER * fh)
    bottom = int(y2 + BODY_HEIGHT_FACE_MULTIPLIER * fh)
    box = (max(0, cx-half), max(0, top), min(width, cx+half), min(height, bottom))
    anchor = (int((box[0] + box[2]) / 2), int(box[1] + 0.68 * (box[3] - box[1])))
    return anchor, box


def analyze_body_regions(image, face_detections, profile_name=None):
    height, width = image.shape[:2]
    profile_name = profile_name or DEFAULT_CAMERA_PROFILE
    boundaries = get_polygons(width, height, profile_name)
    counts = {name: 0 for name in ZONE_ORDER}
    fallbacks = 0
    body_items = []
    for index, detection in enumerate(face_detections, 1):
        bbox = detection["bbox"]
        x1, y1, x2, y2 = map(int, bbox)
        face_center = ((x1 + x2) // 2, (y1 + y2) // 2)

        # Body position is still estimated for visualization and diagnostics.
        body_anchor, body_box = _grabcut_body_anchor(image, bbox)
        used_fallback = body_anchor is None
        if used_fallback:
            body_anchor, body_box = _geometric_body_fallback(image.shape, bbox)
            fallbacks += 1

        # IMPORTANT: the user's marked lines were drawn through face positions.
        # Therefore zone membership uses the face center against those lines.
        # This prevents the lower torso anchor from shifting a back-row face
        # across the front/back boundary. Body anchor remains available in the
        # report/overlay and can be used later to refine seat-row geometry.
        region = point_region(face_center, boundaries)
        counts[region] += 1
        body_items.append({
            "index": index,
            "face_bbox": (x1, y1, x2, y2),
            "face_center": face_center,
            "anchor": body_anchor,
            "box": body_box,
            "region": region,
            "fallback": used_fallback,
        })

    assigned = sum(counts.values())
    stats = {
        "total": assigned,
        "face_anchors": len(face_detections),
        "unassigned": len(face_detections) - assigned,
        "fallbacks": fallbacks,
        "regions": counts,
        "body_items": body_items,
        "camera_profile": profile_name,
        "polygons": boundaries,
        "assignment_basis": "face_center_on_user_marked_boundary; body_anchor_for_visualization",
    }
    return render_body_regions(image, stats), stats


def render_body_regions(image, stats):
    """Draw body estimates, but visibly attach each zone label to its face.

    Zone membership is decided ONLY by face_center in analyze_body_regions().
    GrabCut/geometric body boxes are visualization aids and never reassign a
    person to another zone.
    """
    out = image.copy()
    for item in stats.get("body_items", []):
        bx1, by1, bx2, by2 = item["box"]
        fx1, fy1, fx2, fy2 = item["face_bbox"]
        fx, fy = item["face_center"]
        anchor = item["anchor"]
        region = item["region"]
        color = REGION_COLORS[region]

        # Body estimate: thin outline, not the assignment reference.
        cv2.rectangle(out, (bx1, by1), (bx2, by2), color, 1, cv2.LINE_AA)

        # Face rectangle and centre are the authoritative assignment cue.
        cv2.rectangle(out, (fx1, fy1), (fx2, fy2), color, 2, cv2.LINE_AA)
        cv2.circle(out, (int(fx), int(fy)), 5, (0, 255, 255), -1, cv2.LINE_AA)

        # Body anchor is displayed separately; it does not decide the zone.
        cv2.circle(out, (int(anchor[0]), int(anchor[1])), 4,
                   (255, 255, 255), -1, cv2.LINE_AA)

        suffix = " [geom]" if item["fallback"] else ""
        label = f"FACE P{item['index']} -> {region}{suffix}"
        label_y = max(18, fy1 - 7)
        cv2.putText(out, label, (max(4, fx1), label_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.43, color, 2, cv2.LINE_AA)

    return _draw_zone_overlay(
        out, stats["polygons"], stats["regions"], "Faces assigned",
        stats.get("camera_profile", DEFAULT_CAMERA_PROFILE)
    )


def write_report(path, stats, method):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as report:
        report.write("===== CLASSROOM OCCUPANCY REPORT =====\n")
        report.write(f"Method: {method}\n")
        report.write(f"Camera profile: {stats.get('camera_profile', DEFAULT_CAMERA_PROFILE)}\n")
        report.write(f"Faces detected: {stats['face_anchors']}\n")
        report.write(f"Total assigned persons: {stats['total']}\n")
        report.write(f"Unassigned: {stats['unassigned']}\n")
        report.write(f"Assignment basis: {stats.get('assignment_basis', 'face center')}\n\n")
        for name in ZONE_ORDER:
            report.write(f"{name}: {stats['regions'][name]}\n")
        report.write(f"\nGrabCut fallbacks: {stats['fallbacks']}\n")
        report.write("Zone assignment: face center is compared with the manually marked camera-view boundaries.\n")
        report.write("Body anchor: GrabCut torso estimate, with geometric fallback, retained for body visualization.\n")
        report.write("Zero-unassigned is guaranteed by the four-zone partition; physical correctness should be checked on the overlays.\n")
