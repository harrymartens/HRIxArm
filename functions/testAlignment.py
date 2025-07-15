import cv2
from pyfiglet import Figlet


from ImageGeneration.generateImageOpenAI import edit_image_gpt_image_1
from HelperFunctions.helperFunctions import base64_to_mat, mat_to_base64, show_images, base64_to_buffer
from ImageToVectorConversion.processImage import processImage
from UserInput.inputController import receiveInput
from RoboticPathMovement.moveRobot import draw_contours
from PhotoCapture.photoCapture import capturePhoto
from PhotoCapture.identifyMarkers import scanImageAndCrop

from RoboticPathMovement.robotConfig import RoboticArm


def main():
    arm = RoboticArm()
    arm.reset_position()
    
    arm.calibrate_corners()
    arm.reset_position()
    
        
        
if __name__ == "__main__":
    main()