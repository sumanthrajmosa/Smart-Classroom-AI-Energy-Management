"""
face_detector.py

Enhanced Face Detection using InsightFace

Features:
- Upscaling for small/far faces
- Overlapping tiles
- Multiple detection passes
- Duplicate removal using NMS
- Returns coordinates in original image
"""

import cv2
import numpy as np

from insightface.app import FaceAnalysis

from config import (
    FACE_CONFIDENCE,
    DETECTION_SCALE,
    TILE_SIZE,
    TILE_OVERLAP,
)


class FaceDetector:

    def __init__(self):

        print("[INFO] Loading InsightFace model...")

        self.app = FaceAnalysis(
            name="buffalo_l",
            providers=["CPUExecutionProvider"]
        )

        self.app.prepare(
            ctx_id=0,
            det_size=(640, 640)
        )

        print("[INFO] Face detector ready.")

    # ==========================================================
    # Detect faces in one image
    # ==========================================================

    def _detect_single(self, image):

        faces = self.app.get(image)

        detections = []

        for face in faces:

            score = float(face.det_score)

            if score < FACE_CONFIDENCE:
                continue

            x1, y1, x2, y2 = face.bbox.astype(int)

            detections.append({
                "bbox": (x1, y1, x2, y2),
                "score": score
            })

        return detections

    # ==========================================================
    # Generate overlapping tiles
    # ==========================================================

    def _generate_tiles(self, width, height):

        tiles = []

        step = int(TILE_SIZE * (1 - TILE_OVERLAP))

        # Make sure step is never zero
        step = max(step, 1)

        for y in range(0, height, step):

            for x in range(0, width, step):

                x2 = min(
                    x + TILE_SIZE,
                    width
                )

                y2 = min(
                    y + TILE_SIZE,
                    height
                )

                # Adjust tile start if at image boundary
                x1 = max(
                    0,
                    x2 - TILE_SIZE
                )

                y1 = max(
                    0,
                    y2 - TILE_SIZE
                )

                tiles.append(
                    (x1, y1, x2, y2)
                )

                if x2 == width:
                    break

            if y2 == height:
                break

        # Remove duplicates
        tiles = list(dict.fromkeys(tiles))

        return tiles

    # ==========================================================
    # Remove duplicate face detections
    # ==========================================================

    def _remove_duplicates(self, detections):

        if len(detections) == 0:
            return []

        boxes = []
        scores = []

        for det in detections:

            x1, y1, x2, y2 = det["bbox"]

            boxes.append([
                x1,
                y1,
                x2 - x1,
                y2 - y1
            ])

            scores.append(
                det["score"]
            )

        boxes = np.array(
            boxes,
            dtype=np.float32
        )

        scores = np.array(
            scores,
            dtype=np.float32
        )

        # NMS threshold
        indices = cv2.dnn.NMSBoxes(
            boxes.tolist(),
            scores.tolist(),
            FACE_CONFIDENCE,
            0.35
        )

        if len(indices) == 0:
            return []

        indices = np.array(
            indices
        ).reshape(-1)

        final_detections = []

        for index in indices:

            final_detections.append(
                detections[int(index)]
            )

        # Sort from left to right, then top to bottom
        final_detections.sort(
            key=lambda d: (
                d["bbox"][1],
                d["bbox"][0]
            )
        )

        return final_detections

    # ==========================================================
    # Main face detection
    # ==========================================================

    def detect_faces(self, image):

        original_height, original_width = image.shape[:2]

        print(
            f"[INFO] Original image: "
            f"{original_width} x {original_height}"
        )

        # ------------------------------------------------------
        # Upscale image
        # ------------------------------------------------------

        scaled_width = int(
            original_width * DETECTION_SCALE
        )

        scaled_height = int(
            original_height * DETECTION_SCALE
        )

        scaled_image = cv2.resize(
            image,
            (scaled_width, scaled_height),
            interpolation=cv2.INTER_CUBIC
        )

        print(
            f"[INFO] Detection image: "
            f"{scaled_width} x {scaled_height}"
        )

        # ------------------------------------------------------
        # Generate overlapping tiles
        # ------------------------------------------------------

        tiles = self._generate_tiles(
            scaled_width,
            scaled_height
        )

        print(
            f"[INFO] Detection tiles: {len(tiles)}"
        )

        all_detections = []

        # ------------------------------------------------------
        # Detect faces in every tile
        # ------------------------------------------------------

        for tile_number, tile in enumerate(tiles):

            tx1, ty1, tx2, ty2 = tile

            tile_image = scaled_image[
                ty1:ty2,
                tx1:tx2
            ]

            if tile_image.size == 0:
                continue

            tile_detections = self._detect_single(
                tile_image
            )

            # Convert tile coordinates
            # back to scaled-image coordinates
            for det in tile_detections:

                x1, y1, x2, y2 = det["bbox"]

                x1 += tx1
                x2 += tx1

                y1 += ty1
                y2 += ty1

                all_detections.append({

                    "bbox": (
                        x1,
                        y1,
                        x2,
                        y2
                    ),

                    "score": det["score"]

                })

        print(
            f"[INFO] Raw detections: "
            f"{len(all_detections)}"
        )

        # ------------------------------------------------------
        # Convert coordinates back to original image
        # ------------------------------------------------------

        original_detections = []

        for det in all_detections:

            x1, y1, x2, y2 = det["bbox"]

            x1 = int(x1 / DETECTION_SCALE)
            y1 = int(y1 / DETECTION_SCALE)
            x2 = int(x2 / DETECTION_SCALE)
            y2 = int(y2 / DETECTION_SCALE)

            # Keep coordinates inside image
            x1 = max(
                0,
                min(x1, original_width - 1)
            )

            y1 = max(
                0,
                min(y1, original_height - 1)
            )

            x2 = max(
                0,
                min(x2, original_width)
            )

            y2 = max(
                0,
                min(y2, original_height)
            )

            if x2 <= x1 or y2 <= y1:
                continue

            original_detections.append({

                "bbox": (
                    x1,
                    y1,
                    x2,
                    y2
                ),

                "score": det["score"]

            })

        # ------------------------------------------------------
        # Remove duplicate detections
        # ------------------------------------------------------

        final_detections = self._remove_duplicates(
            original_detections
        )

        print(
            f"[INFO] Final unique faces: "
            f"{len(final_detections)}"
        )

        return final_detections

    # ==========================================================
    # Draw face squares
    # ==========================================================

    def draw_faces(
        self,
        image,
        detections
    ):

        output = image.copy()

        for index, det in enumerate(detections):

            x1, y1, x2, y2 = det["bbox"]

            score = det["score"]

            # ----------------------------------------------
            # Make a SQUARE around the face
            # ----------------------------------------------

            width = x2 - x1
            height = y2 - y1

            size = max(
                width,
                height
            )

            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            square_x1 = center_x - size // 2
            square_y1 = center_y - size // 2

            square_x2 = square_x1 + size
            square_y2 = square_y1 + size

            # Keep square inside image

            square_x1 = max(
                0,
                square_x1
            )

            square_y1 = max(
                0,
                square_y1
            )

            square_x2 = min(
                output.shape[1] - 1,
                square_x2
            )

            square_y2 = min(
                output.shape[0] - 1,
                square_y2
            )

            # ----------------------------------------------
            # Draw square
            # ----------------------------------------------

            cv2.rectangle(
                output,
                (square_x1, square_y1),
                (square_x2, square_y2),
                (0, 255, 0),
                2
            )

            # ----------------------------------------------
            # Face number
            # ----------------------------------------------

            cv2.putText(
                output,
                f"Face {index + 1}",
                (
                    square_x1,
                    max(
                        square_y1 - 8,
                        20
                    )
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2
            )

        # ----------------------------------------------
        # Total face count
        # ----------------------------------------------

        cv2.putText(
            output,
            f"Faces Detected: {len(detections)}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            3
        )

        return output


if __name__ == "__main__":

    import cv2

    detector = FaceDetector()

    image = cv2.imread(
        "input/classroom.jpg"
    )

    if image is None:

        print("Image not found.")

        exit()

    detections = detector.detect_faces(
        image
    )

    print(
        f"\nTotal faces detected: "
        f"{len(detections)}"
    )

    output = detector.draw_faces(
        image,
        detections
    )

    cv2.imwrite(
        "output/detected_faces.jpg",
        output
    )

    cv2.imshow(
        "Detected Faces",
        output
    )

    cv2.waitKey(0)

    cv2.destroyAllWindows()