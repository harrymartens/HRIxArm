import cv2 as cv
import numpy as np
import random

def extract_contours_from_canny(canny_img):
    """
    Given a binary Canny edge image (black background with white single-pixel lines),
    this function iterates over the image and, for every white pixel not yet part of a
    contour, collects all connected white pixels (including diagonals) via DFS.
    
    Then it reorders those points using a nearest-neighbor algorithm. If the next
    candidate point is farther than a set threshold, the current segment is ended,
    and the remainder is processed as a separate segment.
    
    Returns:
      contours: A list of segments, where each segment is an ordered list of (x, y) tuples.
    """
    h, w = canny_img.shape
    visited = np.zeros((h, w), dtype=bool)
    contours = []
    
    # Define 8-connected neighbor offsets.
    neighbor_offsets = [(-1, -1), (-1, 0), (-1, 1),
                        ( 0, -1),           ( 0, 1),
                        ( 1, -1), ( 1, 0),  ( 1, 1)]
    
    def dfs(start_i, start_j):
        """Collect all connected white pixels (as (x,y) with x=column, y=row) starting from (start_i, start_j)."""
        contour = []
        stack = [(start_i, start_j)]
        
        while stack:
            i, j = stack.pop()
            if visited[i, j]:
                continue
            visited[i, j] = True
            contour.append((j, i))  # store as (x, y)
            for di, dj in neighbor_offsets:
                ni, nj = i + di, j + dj
                if 0 <= ni < h and 0 <= nj < w:
                    if not visited[ni, nj] and canny_img[ni, nj] != 0:
                        stack.append((ni, nj))
        return contour

    def reorder_contour(points):
        """
        Reorder a list of points using a nearest neighbor approach. If the nearest unvisited
        point is too far (exceeding a maximum squared distance), break the chain and start
        a new segment.
        
        Returns a list of segments.
        """
        # Maximum allowed squared distance between connected points.
        # Since adjacent pixels are 1 or sqrt(2) apart, a threshold of 5 works well.
        max_distance_sq = 5  
        segments = []
        # Work on a copy so as not to modify the original list.
        points = points.copy()
        
        while points:
            current_segment = []
            # Start with the first available point.
            current = points.pop(0)
            current_segment.append(current)
            while points:
                nearest_index = None
                nearest_distance = None
                for i, pt in enumerate(points):
                    dx = pt[0] - current[0]
                    dy = pt[1] - current[1]
                    dist_sq = dx*dx + dy*dy
                    if nearest_distance is None or dist_sq < nearest_distance:
                        nearest_distance = dist_sq
                        nearest_index = i
                # If the nearest point is within the allowed distance, add it.
                if nearest_distance is not None and nearest_distance <= max_distance_sq:
                    current = points.pop(nearest_index)
                    current_segment.append(current)
                else:
                    # Otherwise, break this segment and start a new one.
                    break
            segments.append(current_segment)
        return segments

    # Iterate over every pixel.
    for i in range(h):
        for j in range(w):
            if canny_img[i, j] != 0 and not visited[i, j]:
                raw_contour = dfs(i, j)
                if len(raw_contour) > 1:
                    # Reorder the DFS points using nearest neighbor.
                    ordered_segments = reorder_contour(raw_contour)
                    for seg in ordered_segments:
                        # Only add segments with at least 2 points.
                        if len(seg) > 1:
                            contours.append(seg)
    return contours
    
def findConnectedComponents(line_image):
    
    segs = extract_contours_from_canny(line_image)
    lineImage = np.zeros((line_image.shape[0], line_image.shape[1], 3), dtype=np.uint8)
 
    for seg in segs:
        pts = np.array(seg, dtype=np.int32).reshape((-1, 1, 2))
        color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        cv.polylines(lineImage, [pts], isClosed=False, color=color, thickness=1)
    
    return segs, lineImage