"""
anonymizer.py

Face anonymization module
"""

import cv2
import numpy as np


class FaceAnonymizer:

    def __init__(self):

        print(
            "[INFO] Face anonymizer loaded."
        )

    def anonymize_face(self, face):

        """
        Input:
            face image

        Output:
            anonymized face
        """

        # Resize to standard size

        face = cv2.resize(
            face,
            (256, 256)
        )

        # Downsample

        low = cv2.resize(
            face,
            (64, 64),
            interpolation=cv2.INTER_AREA
        )

        # Strong blur

        low = cv2.GaussianBlur(
            low,
            (21, 21),
            0
        )

        # Random color variation

        noise = np.random.randint(
            -20,
            20,
            low.shape,
            dtype=np.int16
        )

        temp = low.astype(
            np.int16
        )

        temp = temp + noise

        temp = np.clip(
            temp,
            0,
            255
        )

        low = temp.astype(
            np.uint8
        )

        # Restore size

        restored = cv2.resize(
            low,
            (256, 256),
            interpolation=cv2.INTER_CUBIC
        )

        # Slight smoothing

        restored = cv2.bilateralFilter(
            restored,
            9,
            75,
            75
        )

        return restored

    def replace_face(
        self,
        image,
        bbox,
        anonymized_face
    ):

        x1, y1, x2, y2 = bbox

        # Keep coordinates inside image

        x1 = max(
            0,
            x1
        )

        y1 = max(
            0,
            y1
        )

        x2 = min(
            image.shape[1],
            x2
        )

        y2 = min(
            image.shape[0],
            y2
        )

        if x2 <= x1 or y2 <= y1:
            return image

        width = x2 - x1
        height = y2 - y1

        anonymized_face = cv2.resize(
            anonymized_face,
            (width, height),
            interpolation=cv2.INTER_LINEAR
        )

        image[
            y1:y2,
            x1:x2
        ] = anonymized_face

        return image

    def anonymize_image(
        self,
        image,
        detections
    ):

        output = image.copy()

        face_count = 0

        for det in detections:

            bbox = det["bbox"]

            x1, y1, x2, y2 = bbox

            # Keep coordinates valid
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(image.shape[1], x2)
            y2 = min(image.shape[0], y2)

            if x2 <= x1 or y2 <= y1:
                continue

            face = output[y1:y2, x1:x2]

            if face.size == 0:
                continue

            # Anonymize face
            anon = self.anonymize_face(face)

            output = self.replace_face(
                output,
                (x1, y1, x2, y2),
                anon
            )

            # Draw bounding box around anonymized face
            cv2.rectangle(
                output,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            face_count += 1

        # Display occupancy count
        cv2.putText(
            output,
            f"Occupancy: {face_count}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2,
            cv2.LINE_AA
        )

        return output

if __name__ == "__main__":

    import cv2

    from face_detector import FaceDetector

    detector = FaceDetector()

    anonymizer = FaceAnonymizer()

    img = cv2.imread(
        "input/classroom.jpg"
    )

    if img is None:

        print(
            "Image not found."
        )

        exit()

    detections = detector.detect_faces(
        img
    )

    result = anonymizer.anonymize_image(
        img,
        detections
    )

    cv2.imshow(
        "Anonymized",
        result
    )

    cv2.waitKey(0)

    cv2.destroyAllWindows()