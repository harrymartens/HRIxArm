from HRIxArm.RoboticPathMovement.planErasePath import eraseImage
import cv2


from HelperFunctions.helperFunctions import base64_to_mat, mat_to_base64, show_images, base64_to_buffer

from PhotoCapture.photoCapture import capturePhoto
from PhotoCapture.identifyMarkers import scanImageAndCrop
from RoboticPathMovement.robotConfig import RoboticArm



arm = RoboticArm()

arm.reset_position()

current_image = capturePhoto()

cropped_image = scanImageAndCrop(current_image)
    
flipped_image = cv2.flip(cropped_image, -1)



eraseImage(arm, flipped_image,
            eraser_w_px=30,
            eraser_h_px=20,
            step_ratio=0.9,
            visualize=True)

