def map_pixel_to_robot(pixel, min_x, max_x, min_y, max_y, scaling_factor):
    """
    Maps a pixel coordinate (x, y) from the image coordinate space to the robot drawing area,
    scaling the image as large as possible (covering the canvas) while maintaining its aspect ratio.
    Coordinates are then clamped to lie within [min_x, max_x] and [min_y, max_y].

    Parameters:
      pixel: Tuple (x, y) representing the pixel coordinate.
      drawing_width: Width of the original image.
      drawing_height: Height of the original image.
      min_x, max_x: Horizontal limits of the drawing area.
      min_y, max_y: Vertical limits of the drawing area.
      
    Returns:
      Tuple (x_robot, y_robot) with coordinates in the robot's drawing space.
    """
    x_pixel, y_pixel = pixel

    x_robot = min_x + x_pixel * scaling_factor
    y_robot = min_y + y_pixel * scaling_factor

    # Clamp the coordinates to ensure they lie within the drawing area.
    x_robot = max(min_x, min(max_x, x_robot))
    y_robot = max(min_y, min(max_y, y_robot))

    return int(x_robot), int(y_robot)


import cv2
import numpy as np

def simplify_segment(segment, epsilon=2.0):
    """
    Simplifies a list of (x, y) points using the Ramer-Douglas-Peucker algorithm.
    """
    if len(segment) < 3:
        return segment  # Not enough points to simplify

    # Convert to format required by cv2.approxPolyDP
    pts = np.array(segment, dtype=np.int32).reshape((-1, 1, 2))
    simplified = cv2.approxPolyDP(pts, epsilon=epsilon, closed=False)
    
    # Reshape back to (x, y) tuples
    return [tuple(pt[0]) for pt in simplified]

def executeDrawingCommands(arm, segments, img_shape, simplify=True, epsilon=2.0):
    """
    Draws simplified segments to reduce movement overhead.
    """
    canvas_min_x = arm.min_x
    canvas_max_x = arm.max_x
    canvas_min_y = arm.min_y
    canvas_max_y = arm.max_y

    canvas_width = canvas_max_x - canvas_min_x
    canvas_height = canvas_max_y - canvas_min_y

    drawing_height, drawing_width = img_shape
    scale_x = canvas_width / drawing_width
    scale_y = canvas_height / drawing_height
    scaling_factor = min(scale_x, scale_y)

    for seg in segments:
        if not seg:
            continue

        # Optionally simplify the segment
        if simplify:
            seg = simplify_segment(seg, epsilon=epsilon)

        print(f"Drawing Line Segment with {len(seg)} points.")

        first_pt = seg[0]
        start_x, start_y = map_pixel_to_robot(first_pt,
                                              canvas_min_x, canvas_max_x,
                                              canvas_min_y, canvas_max_y,
                                              scaling_factor)
        arm.set_position(start_x, start_y, draw=False)

        for pt in seg:
            x_robot, y_robot = map_pixel_to_robot(pt,
                                                  canvas_min_x, canvas_max_x,
                                                  canvas_min_y, canvas_max_y,
                                                  scaling_factor)
            arm.set_position(x_robot, y_robot, draw=True)

        arm.set_position(x_robot, y_robot, draw=False)
        
def draw_contours(arm, contours, lineImageShape):
        executeDrawingCommands(arm, contours, lineImageShape)
