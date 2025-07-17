import cv2
import numpy as np
import random

from .moveRobot import draw_contours
from ImageToVectorConversion.openCVImageEditting import binarize_drawing

def plan_eraser_centers(bin_img, rect_w, rect_h, step_ratio):
    """
    Slide a fixed-size window over the binary image in a zig-zag pattern.
    Return two lists:
      - centers: center point of each window that contains any drawn pixel
      - rects: corresponding top-left coordinates of those windows
    """
    h, w = bin_img.shape
    step_x = max(1, int(rect_w * step_ratio))
    step_y = max(1, int(rect_h * step_ratio))
    centers = []
    rects = []
    flip = False
    for y in range(0, h - rect_h + 1, step_y):
        xs = list(range(0, w - rect_w + 1, step_x))
        if flip:
            xs = xs[::-1]
        flip = not flip
        for x in xs:
            window = bin_img[y:y+rect_h, x:x+rect_w]
            if np.any(window):
                cx = x + rect_w // 2
                cy = y + rect_h // 2
                centers.append((cx, cy))
                rects.append((x, y))
    return centers, rects

def eraseImage(arm, img, eraser_w_px=50, eraser_h_px=30, step_ratio=0.5, visualize=True):
    bin_img = binarize_drawing(img)
    
    
    # 2) Plan eraser centers and rectangles
    centers, rects = plan_eraser_centers(bin_img, eraser_w_px, eraser_h_px, step_ratio)
    # 3) Treat all centers as one continuous path
    segments = [centers]

    # 4) Visualization
    if visualize:
        vis = img.copy()
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
    # draw_contours(arm, segments, bin_img.shape[:2])
