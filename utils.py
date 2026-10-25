"""
utils.py
Utility functions for FacePrivacy Project
"""

import cv2
import os


def load_image(image_path):
    """
    Load an image from disk.
    """

    if not os.path.exists(image_path):
        raise FileNotFoundError(
            f"Image not found : {image_path}"
        )

    img = cv2.imread(image_path)

    if img is None:
        raise Exception(
            "Unable to read image."
        )

    return img


def save_image(path, image):
    """
    Save image.
    """

    folder = os.path.dirname(path)

    if folder != "":
        os.makedirs(folder, exist_ok=True)

    cv2.imwrite(path, image)


def write_occupancy(path, stats):
    """
    Save occupancy count.
    """

    with open(path, "w") as f:
        f.write("===== Occupancy Report =====\n")
        if isinstance(stats, int):
            f.write(f"Persons Detected : {stats}\n")
        else:
            f.write(f"Total Persons Detected : {stats['total']}\n")
            f.write(f"Left Side : {stats['left']}\n")
            f.write(f"Right Side : {stats['right']}\n")
            for i, count in enumerate(stats['rows']):
                f.write(f"Row {i+1} : {count}\n")


def draw_box(
    image,
    x1,
    y1,
    x2,
    y2,
    color=(0, 255, 0),
    thickness=2,
):

    cv2.rectangle(
        image,
        (x1, y1),
        (x2, y2),
        color,
        thickness,
    )


def put_text(
    image,
    text,
    x,
    y,
    color=(0, 255, 255),
):

    cv2.putText(
        image,
        text,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        color,
        2,
    )


def blur_face(face):

    return cv2.GaussianBlur(
        face,
        (99, 99),
        30,
    )


def pixelate_face(face, blocks=12):
    """
    Pixelate face.
    """

    h, w = face.shape[:2]

    temp = cv2.resize(
        face,
        (blocks, blocks),
        interpolation=cv2.INTER_LINEAR,
    )

    pixelated = cv2.resize(
        temp,
        (w, h),
        interpolation=cv2.INTER_NEAREST,
    )

    return pixelated


def resize_face(face, size=256):

    return cv2.resize(
        face,
        (size, size),
        interpolation=cv2.INTER_LINEAR,
    )


def crop_face(image, bbox):

    x1, y1, x2, y2 = bbox

    return image[y1:y2, x1:x2]


def paste_face(image, face, bbox):

    x1, y1, x2, y2 = bbox

    face = cv2.resize(
        face,
        (x2 - x1, y2 - y1)
    )

    image[y1:y2, x1:x2] = face

    return image


def show(title, image):

    cv2.imshow(title, image)

    cv2.waitKey(0)

    cv2.destroyAllWindows()


def count_people(results):

    total = 0

    for box in results.boxes:

        cls = int(box.cls[0])

        if cls == 0:
            total += 1

    return total


def analyze_and_draw_regions(image, detections):
    """
    Draw polygon zones and display occupancy counts per region.
    Row 1: Left side 1st 3 benches
    Row 2: Right side 1st 3 benches
    Row 3: Left side last benches
    Row 4: Right side last benches
    """
    import numpy as np
    
    h, w = image.shape[:2]
    
    # Define exact polygon zones for the physical benches
    mid_x = 800
    left_split_y = 645  # Y-coordinate splitting left front and back benches
    right_split_y = 700 # Y-coordinate splitting right front and back benches
    
    poly_left_front = np.array([[0, left_split_y], [mid_x, left_split_y], [mid_x, h], [0, h]], np.int32)
    poly_left_back = np.array([[0, 0], [mid_x, 0], [mid_x, left_split_y], [0, left_split_y]], np.int32)
    poly_right_front = np.array([[mid_x, right_split_y], [w, right_split_y], [w, h], [mid_x, h]], np.int32)
    poly_right_back = np.array([[mid_x, 0], [w, 0], [w, right_split_y], [mid_x, right_split_y]], np.int32)
    
    left_count = 0
    right_count = 0
    row_counts = [0, 0, 0, 0] # Left Front, Right Front, Left Back, Right Back
    
    valid_detections = 0
    
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        
        # Filter out unusually large faces (e.g., the teacher in the foreground)
        box_area = (x2 - x1) * (y2 - y1)
        if box_area > 20000: # 20000 pixels is roughly a 140x140 face, teacher's is much larger
            continue
            
        valid_detections += 1
            
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        
        if cv2.pointPolygonTest(poly_left_front, (cx, cy), False) >= 0:
            left_count += 1
            row_counts[0] += 1
        elif cv2.pointPolygonTest(poly_right_front, (cx, cy), False) >= 0:
            right_count += 1
            row_counts[1] += 1
        elif cv2.pointPolygonTest(poly_left_back, (cx, cy), False) >= 0:
            left_count += 1
            row_counts[2] += 1
        elif cv2.pointPolygonTest(poly_right_back, (cx, cy), False) >= 0:
            right_count += 1
            row_counts[3] += 1
                
    # Draw zones
    overlay = image.copy()
    cv2.fillPoly(overlay, [poly_left_front], (0, 255, 0))   # Green
    cv2.fillPoly(overlay, [poly_right_front], (255, 0, 0))  # Blue
    cv2.fillPoly(overlay, [poly_left_back], (0, 128, 0))    # Dark Green
    cv2.fillPoly(overlay, [poly_right_back], (128, 0, 0))   # Dark Blue
    
    # Blend overlay with original image
    cv2.addWeighted(overlay, 0.2, image, 0.8, 0, image)
    
    # Draw splitting lines
    cv2.line(image, (mid_x, 0), (mid_x, h), (0, 255, 255), 3) # Center aisle
    cv2.line(image, (0, left_split_y), (mid_x, left_split_y), (0, 255, 255), 3) # Left horizontal split
    cv2.line(image, (mid_x, right_split_y), (w, right_split_y), (0, 255, 255), 3) # Right horizontal split
        
    # Put text
    cv2.putText(image, f"Left: {left_count}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 3)
    cv2.putText(image, f"Right: {right_count}", (mid_x + 10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 3)
    
    cv2.putText(image, f"Row 1 (Left 1st 3): {row_counts[0]}", (10, h - 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 3)
    cv2.putText(image, f"Row 2 (Right 1st 3): {row_counts[1]}", (mid_x + 10, h - 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 3)
    cv2.putText(image, f"Row 3 (Left Last 3): {row_counts[2]}", (10, left_split_y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 3)
    cv2.putText(image, f"Row 4 (Right Last 3): {row_counts[3]}", (mid_x + 10, right_split_y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 3)
        
    stats = {
        'total': valid_detections,
        'left': left_count,
        'right': right_count,
        'rows': row_counts
    }
    
    return image, stats