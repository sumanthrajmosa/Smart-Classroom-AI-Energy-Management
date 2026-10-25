"""
main.py

Face Privacy Pipeline

Flow:

classroom.jpg
      ↓
Enhanced Face Detection
      ↓
Person Count = Face Count
      ↓
Face Anonymization
      ↓
Save anonymized.jpg
      ↓
Draw detected face squares
      ↓
Save detected.jpg
      ↓
Save occupancy.txt
"""

import os

from config import (
    INPUT_IMAGE,
    ANONYMIZED_IMAGE,
    DETECTED_IMAGE,
    OCCUPANCY_FILE,
)

from utils import (
    load_image,
    save_image,
    write_occupancy,
    analyze_and_draw_regions,
)

from face_detector import FaceDetector
from anonymizer import FaceAnonymizer


def main():

    print("=" * 60)
    print("FACE PRIVACY SYSTEM")
    print("=" * 60)

    # ==========================================================
    # Check input image
    # ==========================================================

    if not os.path.exists(INPUT_IMAGE):

        print("\nInput image not found!")

        print(
            f"Place classroom.jpg here:"
        )

        print(INPUT_IMAGE)

        return

    # ==========================================================
    # Load image
    # ==========================================================

    print("\n[1] Loading classroom image...")

    image = load_image(
        INPUT_IMAGE
    )

    print(
        f"Image size: "
        f"{image.shape[1]} x {image.shape[0]}"
    )

    # ==========================================================
    # Face Detection
    # ==========================================================

    print("\n[2] Detecting faces...")

    detector = FaceDetector()

    detections = detector.detect_faces(
        image
    )

    # ==========================================================
    # Person Count
    # ==========================================================

    person_count = len(
        detections
    )

    print(
        f"\nFaces Detected : "
        f"{person_count}"
    )

    print(
        f"Person Count   : "
        f"{person_count}"
    )

    # ==========================================================
    # Create detection visualization
    # ==========================================================

    print(
        "\n[3] Drawing face detection squares..."
    )

    detected_image = detector.draw_faces(
        image,
        detections
    )

    detected_image, stats = analyze_and_draw_regions(
        detected_image,
        detections
    )

    save_image(
        DETECTED_IMAGE,
        detected_image
    )

    print(
        f"Detection image saved:"
    )

    print(
        DETECTED_IMAGE
    )

    # ==========================================================
    # Face Anonymization
    # ==========================================================

    print(
        "\n[4] Anonymizing detected faces..."
    )

    anonymizer = FaceAnonymizer()

    anonymized = anonymizer.anonymize_image(
        image,
        detections
    )

    # ==========================================================
    # Save anonymized image
    # ==========================================================

    save_image(
        ANONYMIZED_IMAGE,
        anonymized
    )

    print(
        "Anonymized image saved:"
    )

    print(
        ANONYMIZED_IMAGE
    )

    # ==========================================================
    # Save occupancy
    # ==========================================================

    print(
        "\n[5] Saving occupancy..."
    )

    write_occupancy(
        OCCUPANCY_FILE,
        stats
    )

    print(
        "Occupancy file saved:"
    )

    print(
        OCCUPANCY_FILE
    )

    # ==========================================================
    # Final Result
    # ==========================================================

    print("\n" + "=" * 60)

    print(
        f"TOTAL PERSONS DETECTED : "
        f"{person_count}"
    )

    print("=" * 60)

    print("\nOutput files:")

    print(
        f"1. {ANONYMIZED_IMAGE}"
    )

    print(
        f"2. {DETECTED_IMAGE}"
    )

    print(
        f"3. {OCCUPANCY_FILE}"
    )

    print(
        "\nFinished Successfully."
    )


if __name__ == "__main__":

    main()