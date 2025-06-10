import cv2
import numpy as np
from pupil_apriltags import Detector

def scanImageAndCrop(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img_uint8 = cv2.convertScaleAbs(gray)

    # Initialize detector
    at_detector = Detector(
        families="tag25h9",
        nthreads=1,
        quad_decimate=1.0,
        quad_sigma=0.0,
        refine_edges=1,
        decode_sharpening=0.25,
        debug=0
    )

    # Detect AprilTags
    detections = at_detector.detect(img_uint8)

    if len(detections) != 4:
        raise ValueError("Expected exactly 4 AprilTags, but found {}".format(len(detections)))

    # Get image center to identify inner corners
    h, w = gray.shape
    center = np.array([w / 2, h / 2])

    # Get the closest corner to the image center for each tag (assumed inner corner)
    inner_corners = []
    for det in detections:
        corners = det.corners  # shape (4, 2)
        # Find corner closest to the center of the image
        distances = np.linalg.norm(corners - center, axis=1)
        inner_corner = corners[np.argmin(distances)]
        inner_corners.append(inner_corner)

    # Order points: top-left, top-right, bottom-right, bottom-left
    def order_points(pts):
        pts = np.array(pts)
        s = pts.sum(axis=1)
        diff = np.diff(pts, axis=1)
        return np.array([
            pts[np.argmin(s)],        # top-left
            pts[np.argmin(diff)],     # top-right
            pts[np.argmax(s)],        # bottom-right
            pts[np.argmax(diff)]      # bottom-left
        ])

    ordered_corners = order_points(inner_corners)

    # Destination rectangle (output image size)
    width = int(np.linalg.norm(ordered_corners[0] - ordered_corners[1]))
    height = int(np.linalg.norm(ordered_corners[0] - ordered_corners[3]))

    dst = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]
    ], dtype="float32")

    # Compute perspective transform
    M = cv2.getPerspectiveTransform(ordered_corners.astype("float32"), dst)
    warped = cv2.warpPerspective(image, M, (width, height))

    cv2.imshow("Warped Image", warped)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return warped