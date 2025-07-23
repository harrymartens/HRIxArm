import cv2
from pyfiglet import Figlet


from Utils.ImageGeneration.generateImageOpenAI import edit_image_gpt_image_1
from Utils.HelperFunctions.helperFunctions import base64_to_mat, mat_to_base64, show_images, base64_to_buffer
from Utils.ImageToVectorConversion.processImage import processImage
from Utils.UserInput.inputController import receiveInput
from Utils.RoboticPathMovement.moveRobot import draw_contours
from Utils.PhotoCapture.photoCapture import capturePhoto
from Utils.PhotoCapture.identifyMarkers import scanImageAndCrop

from Utils.RoboticPathMovement.robotConfig import RoboticArm


def main():
    arm = RoboticArm()
    arm.reset_position()
    arm.centre_position()
    
    arm.calibrate_corners()
    arm.reset_position()
    
        
        
if __name__ == "__main__":
    main()