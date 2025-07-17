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


def executeDrawingCommands(arm, segments, img_shape):
    """
    Given a list of segments (from our edge extraction), this function maps each pixel coordinate 
    to the robot's drawing area and sends movement commands to the robot via its set_position method.
    
    Parameters:
      arm: Instance of RoboticArm.
      segments: List of segments; each segment is an ordered list of (x, y) tuples.
      drawing_width: Width of the image in pixels (default 500).
      drawing_height: Height of the image in pixels (default 500).
    """
    canvas_min_x = arm.min_x
    canvas_max_x = arm.max_x
    canvas_min_y = arm.min_y
    canvas_max_y = arm.max_y
    
    # Dimensions of the drawing area.
    canvas_width = arm.max_x - arm.min_x
    canvas_height = arm.max_y - arm.min_y

    
    drawing_height, drawing_width = img_shape
    
    # Compute scale factors for each axis.
    scale_x = canvas_width / drawing_width
    scale_y = canvas_height / drawing_height
        
    scaling_factor = min(scale_x, scale_y)
    

    for seg in segments:
        if not seg:
            continue  # Skip empty segments
        
        print(f"Drawing Line Segment: {seg}\n\n")
        # Get the first point of the segment and convert it to robot coordinates.
        first_pt = seg[0]  # Each point is now a tuple (x, y)
        start_x, start_y = map_pixel_to_robot(first_pt,
                                                canvas_min_x, canvas_max_x,
                                                canvas_min_y, canvas_max_y,
                                                scaling_factor)
        # Move to the start point with the pen raised.
        arm.set_position(start_x, start_y, draw=False)
        
        # Now iterate over each point in the segment.
        for pt in seg:
            x_robot, y_robot = map_pixel_to_robot(pt,
                                                  canvas_min_x, canvas_max_x,
                                                  canvas_min_y, canvas_max_y,
                                                  scaling_factor)
            # Move with the pen down to draw the line.
            arm.set_position(x_robot, y_robot, draw=True)
        
        # After finishing the segment, lift the pen.
        arm.set_position(x_robot, y_robot, draw=False)
        
def draw_contours(arm, contours, lineImageShape):
        arm.centre_position()
        executeDrawingCommands(arm, contours, lineImageShape)
        arm.centre_position()
        arm.reset_position()