import cv2
from pyfiglet import Figlet
import time


from Utils.ImageGeneration.generateImageOpenAI import edit_image_gpt_image_1
from Utils.HelperFunctions.helperFunctions import base64_to_mat, mat_to_base64, show_images, base64_to_buffer
from Utils.ImageToVectorConversion.processImage import processImage
from Utils.UserInput.inputController import receiveInput
from Utils.RoboticPathMovement.moveRobot import draw_contours
from Utils.PhotoCapture.photoCapture import capturePhoto
from Utils.PhotoCapture.identifyMarkers import scanImageAndCrop
from Utils.RoboticPathMovement.planErasePath import eraseImage

from Utils.RoboticPathMovement.robotConfig import RoboticArm


def main():
    f = Figlet(font="slant")
    print(f.renderText("Robot Drawer"))
    
    arm = RoboticArm()

    arm.intermediate_position()
    arm.change_attachment_position()
    
    _ = receiveInput("Press Enter when eraser is attached")
    arm.change_mode("erase")
    
    arm.intermediate_position()
    arm.reset_position()
    _ = receiveInput("Press Enter when ready to capture photo of canvas?")
    

    photo = capturePhoto()
    while photo is None:
        print("No photo captured. Please try again.")
        photo = capturePhoto()
        
    cropped_image = scanImageAndCrop(photo)
    flipped_image = cv2.flip(cropped_image, -1)
    base64_image = mat_to_base64(flipped_image)
    image_buffer = base64_to_buffer(base64_image)
    
    prompt = receiveInput("How would you like to edit the existing drawing")
    edited_base64 = edit_image_gpt_image_1(image_buffer, prompt)
    
    edited_image = base64_to_mat(edited_base64)
    contours, lineImage = processImage(edited_image)
    
    show_images(edited_image, lineImage, titles=["Edited Image", "Contours"])
    confirmation = receiveInput("Would you like me to draw this image? (yes/no)")
    
    if "no" in confirmation.strip().lower():
        return f"he user rejected the generated image edit before it could be drawn: '{prompt}'."
    
    arm.intermediate_position()
    arm.centre_position()
    
    print("Erasing existing drawing...")
    eraseImage(arm, flipped_image,
            eraser_w_px=80,
            eraser_h_px=40,
            step_ratio=0.9,
            visualize=True)
    
    arm.centre_position()
    arm.change_attachment_position()
    
    _ = receiveInput("Press Enter when pen is attached")
    arm.change_mode("marker")
    arm.centre_position()

    confirmation = receiveInput("Would you like me to start drawing? (yes/no)")
     
    if "no" in confirmation.strip().lower():
        return f"he user rejected the generated image edit before it could be drawn: '{prompt}'."
    
    draw_contours(arm, contours, lineImage.shape[:2])
    arm.centre_position()
    arm.intermediate_position()
    arm.reset_position()

    return f"The drawing of {prompt} has been complete"
        
        
if __name__ == "__main__":
    main()