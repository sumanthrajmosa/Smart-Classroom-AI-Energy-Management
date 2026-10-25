import cv2
import numpy as np
from face_detector import FaceDetector

detector = FaceDetector()
image = cv2.imread("input/classroom.jpg")
if image is None:
    print("Could not load image.")
    exit()

detections = detector.detect_faces(image)

cys = np.array([(det["bbox"][1] + det["bbox"][3]) / 2 for det in detections], dtype=np.float32).reshape(-1, 1)

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
ret, label, center = cv2.kmeans(cys, 6, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

centers = np.sort(center, axis=0).flatten()
print("Cluster centers (benches):", centers)

lines = [(centers[i] + centers[i+1]) / 2 for i in range(5)]
print("Dividing lines:", lines)
