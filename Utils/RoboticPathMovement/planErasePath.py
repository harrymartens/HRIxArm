import cv2
import numpy as np
import random
from scipy.spatial import distance


from .moveRobot import draw_contours
from Utils.ImageToVectorConversion.openCVImageEditting import binarize_drawing

def plan_eraser_centers(bin_img, rect_w, rect_h):
    """
    Plan minimal-movement eraser path using dynamic region coverage.
    Ensures all ink is erased, avoids unnecessary extra steps.
    """
    h, w = bin_img.shape
    covered = np.zeros_like(bin_img, dtype=bool)

    # 1. Get all ink pixel coordinates
    ink_coords = np.argwhere(bin_img > 0)
    if len(ink_coords) == 0:
        return [], []

    erase_centers = []
    rects = []

    # 2. Start from top-left ink pixel
    remaining = set(map(tuple, ink_coords))
    current = min(remaining, key=lambda pt: pt[1] + pt[0])  # top-left
    current = tuple(current)

    def mark_covered(center):
        """Mark the region covered by an erase centered at `center`."""
        cx, cy = center
        x1 = max(0, cx - rect_h // 2)
        y1 = max(0, cy - rect_w // 2)
        x2 = min(h, cx + rect_h // 2)
        y2 = min(w, cy + rect_w // 2)
        covered[x1:x2, y1:y2] = True

    while remaining:
        cx, cy = current
        erase_centers.append((cy, cx))  # switch to (x, y) format for consistency
        rects.append((cy - rect_w // 2, cx - rect_h // 2))
        mark_covered((cx, cy))

        # 3. Remove covered ink pixels
        newly_remaining = []
        for pt in remaining:
            if not covered[pt]:
                newly_remaining.append(pt)
        remaining = set(newly_remaining)

        if not remaining:
            break

        # 4. Pick the nearest uncovered ink point to current position
        dists = distance.cdist([current], list(remaining))
        current = list(remaining)[np.argmin(dists)]

    return erase_centers, rects

def eraseImage(arm, img, eraser_w_px=50, eraser_h_px=30, step_ratio=0.5, visualize=True):
    bin_img = binarize_drawing(img)
    
    bin_img = cv2.flip(bin_img, 0)
    
    # 2) Plan eraser centers and rectangles
    centers, rects = plan_eraser_centers(bin_img, eraser_w_px, eraser_h_px)
    # 3) Treat all centers as one continuous path
    segments = [centers]

    # 4) Visualization
    if visualize:
        vis = img.copy()
        vis = cv2.flip(vis, 0)
        # draw each rectangle window in green
        for (rx, ry) in rects:
            cv2.rectangle(vis, (rx, ry), (rx + eraser_w_px, ry + eraser_h_px), (0,255,0), 1)
        # draw each center in red
        for c in centers:
            cv2.circle(vis, c, radius=2, color=(0,0,255), thickness=-1)
        # draw continuous path in blue
        if len(centers) > 1:
            pts = np.array(centers, dtype=np.int32).reshape(-1,1,2)
            cv2.polylines(vis, [pts], isClosed=False, color=(255,0,0), thickness=1)
        cv2.imshow('Eraser Windows and Continuous Path', vis)
        cv2.waitKey(0)
        cv2.destroyWindow('Eraser Windows and Continuous Path')
    # 6) Erase via draw_contours abstraction
    draw_contours(arm, segments, bin_img.shape[:2])
