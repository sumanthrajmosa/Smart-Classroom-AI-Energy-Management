"""Configuration for Approach B classroom occupancy processing.

The split boundaries are calibrated from the user's marked reference frames.
Zone membership is determined from the FACE CENTER so that a person remains
in the zone indicated by the manually marked face-level boundary. GrabCut/body
anchors are still estimated and visualized, but do not override face-level
zone membership.
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CALIBRATION_DIR = os.path.join(BASE_DIR, "calibration_refs")
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CALIBRATION_DIR, exist_ok=True)

_classroom_image = os.path.join(INPUT_DIR, "classroom.jpg")
_input_image = os.path.join(INPUT_DIR, "input.jpg")
INPUT_IMAGE = _classroom_image if os.path.isfile(_classroom_image) else _input_image
INPUT_COPY = os.path.join(OUTPUT_DIR, "input.jpg")
ANONYMIZED_IMAGE = os.path.join(OUTPUT_DIR, "anonymized.jpg")
DETECTED_IMAGE = os.path.join(OUTPUT_DIR, "detected.jpg")
ZONE_DIVISION_IMAGE = os.path.join(OUTPUT_DIR, "zone_division.jpg")
CLASSROOM_RESULT_IMAGE = os.path.join(OUTPUT_DIR, "classroom_result.jpg")
OCCUPANCY_FILE = os.path.join(OUTPUT_DIR, "occupancy.txt")

# Detection settings are unchanged.
FACE_CONFIDENCE = 0.35
FACE_MODEL = "buffalo_l"
DETECTION_SCALE = 1.5
TILE_SIZE = 960
TILE_OVERLAP = 0.25

CAMERA_REFERENCES = {
    "VIEW_PHOTO7": os.path.join(CALIBRATION_DIR, "photo7.jpg"),
    "VIEW_PHOTO15": os.path.join(CALIBRATION_DIR, "photo15.jpg"),
    "VIEW_PHOTO25": os.path.join(CALIBRATION_DIR, "photo25.jpg"),
}

# Boundary format:
# split_x: normalized x boundary, or points [(normalized_y, normalized_x), ...]
# split_y: normalized y boundary, points [(normalized_x, normalized_y), ...]
#
# PHOTO15 and PHOTO25 coordinates are approximations digitized from the
# user's yellow annotations. The row boundary is face-level by design.
CAMERA_ZONE_PROFILES = {
    "VIEW_PHOTO7": {
        "split_x": 0.50,
        "split_y": 0.44,
    },
    "VIEW_PHOTO15": {
        "split_x": 0.518,
        "split_y_points": [
            (0.00, 0.442),
            (0.25, 0.452),
            (0.50, 0.468),
            (0.75, 0.482),
            (1.00, 0.495),
        ],
    },
    "VIEW_PHOTO25": {
        "split_x": 0.526,
        "split_y_points": [
            (0.00, 0.584),
            (0.25, 0.590),
            (0.50, 0.600),
            (0.75, 0.615),
            (1.00, 0.645),
        ],
    },
}
DEFAULT_CAMERA_PROFILE = "VIEW_PHOTO15"

REGION_COLORS = {
    "BACK_LEFT": (255, 160, 30),
    "BACK_RIGHT": (30, 170, 255),
    "FRONT_LEFT": (50, 210, 70),
    "FRONT_RIGHT": (210, 70, 190),
}

BODY_WIDTH_FACE_MULTIPLIER = 2.8
BODY_HEIGHT_FACE_MULTIPLIER = 4.2
BODY_TOP_FACE_MULTIPLIER = 0.55
