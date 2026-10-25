"""
config.py

Configuration file for the FacePrivacy project.
"""

import os


# ==============================
# Project Directories
# ==============================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

INPUT_DIR = os.path.join(
    BASE_DIR,
    "input"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "output"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)


os.makedirs(
    INPUT_DIR,
    exist_ok=True
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


# ==============================
# Input / Output
# ==============================

INPUT_IMAGE = os.path.join(
    INPUT_DIR,
    "classroom.jpg"
)

ANONYMIZED_IMAGE = os.path.join(
    OUTPUT_DIR,
    "anonymized.jpg"
)

DETECTED_IMAGE = os.path.join(
    OUTPUT_DIR,
    "detected.jpg"
)

OCCUPANCY_FILE = os.path.join(
    OUTPUT_DIR,
    "occupancy.txt"
)


# ==============================
# Face Detection
# ==============================

FACE_CONFIDENCE = 0.35

FACE_MODEL = "buffalo_l"


# ==============================
# Enhanced Detection
# ==============================

# Enlarge image before detection.
#
# 2.0 means:
#
# 1280 x 960
#      ↓
# 2560 x 1920
#
DETECTION_SCALE = 2.0


# Size of each detection tile.
#
# Smaller tiles mean faces occupy
# more pixels inside the detector.
#
TILE_SIZE = 960


# Overlap between adjacent tiles.
#
# 0.30 = 30% overlap
#
TILE_OVERLAP = 0.30


# ==============================
# Face Processing
# ==============================

FACE_SIZE = 256

BLUR_KERNEL = (99, 99)


# ==============================
# GFPGAN
# ==============================

GFPGAN_MODEL = os.path.join(
    MODEL_DIR,
    "GFPGANv1.4.pth"
)

UPSCALE = 2


# ==============================
# Drawing
# ==============================

BOX_COLOR = (0, 255, 0)

BOX_THICKNESS = 2

TEXT_COLOR = (0, 255, 255)

FONT_SCALE = 0.7

FONT_THICKNESS = 2


# ==============================
# Occupancy
# ==============================

SAVE_OCCUPANCY = True

SHOW_RESULTS = True

SAVE_RESULTS = True