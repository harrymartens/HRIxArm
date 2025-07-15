import cv2
from pyfiglet import Figlet


from ImageGeneration.generateImageOpenAI import edit_image_gpt_image_1
from HelperFunctions.helperFunctions import base64_to_mat, mat_to_base64, show_images, base64_to_buffer
from ImageToVectorConversion.processImage import processImage
from UserInput.inputController import receiveInput
from RoboticPathMovement.moveRobot import draw_contours
from PhotoCapture.photoCapture import capturePhoto
from PhotoCapture.identifyMarkers import scanImageAndCrop
from RoboticPathMovement.planErasePath import eraseImage

from RoboticPathMovement.robotConfig import RoboticArm


def main():
    f = Figlet(font="slant")
    print(f.renderText("Robot Drawer"))
    
    arm = RoboticArm()
    arm.reset_position()
    
    photo = capturePhoto()
    if photo is None:
        print("No photo captured. Please try again.")
        
    prompt = receiveInput("How would you like to edit the existing drawing")
        
    
    cropped_image = scanImageAndCrop(photo)
        
    flipped_image = cv2.flip(cropped_image, -1)
    
    base64_image = mat_to_base64(flipped_image)
    
    image_buffer = base64_to_buffer(base64_image)
    
    edited_base64 = edit_image_gpt_image_1(image_buffer, prompt)
    
    edited_image = base64_to_mat(edited_base64)
    
    contours, lineImage = processImage(edited_image)
    
    show_images(edited_image, lineImage, titles=["Edited Image", "Contours"])
    
    confirmation = receiveInput("Would you like me to draw this image? (yes/no)")
    
    if "no" in confirmation.strip().lower():
        return f"he user rejected the generated image edit before it could be drawn: '{prompt}'."
    
    # eraseImage(arm, flipped_image,
    #         eraser_w_px=30,
    #         eraser_h_px=20,
    #         step_ratio=0.9,
    #         visualize=True)

    draw_contours(arm, contours, lineImage.shape[:2])
    return f"The drawing of {prompt} has been complete"
        
        
if __name__ == "__main__":
    main()