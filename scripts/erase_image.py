import cv2

from Utils.RoboticPathMovement.planErasePath import eraseImage

from Utils.HelperFunctions.helperFunctions import base64_to_mat, mat_to_base64, show_images, base64_to_buffer
from Utils.UserInput.inputController import receiveInput
from Utils.PhotoCapture.photoCapture import capturePhoto
from Utils.PhotoCapture.identifyMarkers import scanImageAndCrop
from Utils.RoboticPathMovement.robotConfig import RoboticArm



arm = RoboticArm()

arm.intermediate_position()
arm.change_attachment_position()

_ = receiveInput("Press Enter when Eraser is attached?")

arm.change_mode("erase")
arm.intermediate_position()
arm.reset_position()

_ = receiveInput("Press Enter when ready to capture a image of the canvas?")


current_image = capturePhoto()

cropped_image = scanImageAndCrop(current_image)
    
flipped_image = cv2.flip(cropped_image, -1)

eraseImage(arm, flipped_image,
            eraser_w_px=80,
            eraser_h_px=40,
            step_ratio=0.5,
            visualize=True)

