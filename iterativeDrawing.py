#!/usr/bin/env python3
from pyfiglet import Figlet
import cv2
import numpy as np
import base64
from base64 import b64decode
from io import BytesIO
from openai import OpenAI

from UserInput.inputController import receiveInput
from PhotoCapture.photoCapture import capturePhoto
from PhotoCapture.identifyMarkers import scanImageAndCrop
from ImageToVectorConversion.processImage import processImage
from ImageGeneration.generateImageOpenAI import edit_image_gpt_image_1, generate_image_gpt_image_1, edit_image_responses
from RoboticPathMovement.robotConfig import RoboticArm
from RoboticPathMovement.moveRobot import executeDrawingCommands

client = OpenAI()
roboticArm = RoboticArm()


# === Utility Functions ===
def mat_to_base64(image, ext=".png"):
    success, buffer = cv2.imencode(ext, image)
    if not success:
        raise ValueError("Image encoding failed")
    return base64.b64encode(buffer).decode("utf-8")

def base64_to_mat(base64_string):
    img_data = b64decode(base64_string)
    np_arr = np.frombuffer(img_data, dtype=np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Decoding failed")
    return image

def show_images(*images, titles=None):
    for i, img in enumerate(images):
        title = titles[i] if titles else f"Image {i+1}"
        cv2.imshow(title, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
def draw_contours(contours, lineImage):
    roboticArm.centre_position()
    executeDrawingCommands(roboticArm, contours, lineImage.shape[:2])
    roboticArm.reset_position()
    
    
def generateImage():
    while True:
        prompt = receiveInput("What would you like to draw?")
        
        print("Generating image...")
        image_base64 = generate_image_gpt_image_1(prompt)
        
        
        generated_image = base64_to_mat(image_base64)
        
        
        contours, lineImage = processImage(generated_image)
        
        show_images(generated_image, lineImage, titles=["Generated Image", "Contours"])
        confimration = receiveInput("Would you like me to draw this image? (yes/no)")
        
        if  "yes" in confimration.lower():
            break
    
    draw_contours(contours, lineImage)
            
  
def editImage():
    while True:
        current_image = capturePhoto()
        if current_image is None:
            print("❌ No image captured. Exiting.")
            return
        
        cropped_image = scanImageAndCrop(current_image)
        
        flipped_image = cv2.flip(cropped_image, -1)
        
        base64_image = mat_to_base64(flipped_image)
        img_bytes = b64decode(base64_image)
        image_buffer = BytesIO(img_bytes)
        image_buffer.name = "image.png"  # required by OpenAI
        
        user_prompt = receiveInput("How would you like to alter your image?")
        edited_base64 = edit_image_gpt_image_1(image_buffer, user_prompt)
        edited_image = base64_to_mat(edited_base64)
        contours, lineImage = processImage(edited_image)
        show_images(edited_image, lineImage, titles=["Edited Image", "Contours"])
        
        previous_response = None
        
        while True:
            confirmation = receiveInput("Would you like me to draw this? Or I can also edit the image further (draw/refine)?")
            
            if "draw" in confirmation.lower():
                draw_contours(contours, lineImage)
                leave = receiveInput("Would you like to continue drawing, or exit(continue/exit?")
                if "exit" in leave.lower():
                    print("Thanks for drawing with me! See you next time!")
                    exit(0)
                else:
                    break
            elif "refine" in confirmation.lower():
                prompt = receiveInput("How would you like to further edit the image?")
                edited_base64, previous_response = edit_image_responses(edited_base64, prompt, previous_response)
                edited_image = base64_to_mat(edited_base64)
                contours, lineImage = processImage(edited_image)
                show_images(edited_image, lineImage, titles=["Edited Image", "Contours"])
                
            
            
# === Main Loop ===
def main():
    f = Figlet(font="slant")
    print(f.renderText("Robot Creative Assistant"))
    while True:   
        start = receiveInput("Would you like to generate a new image, or edit an existing?")
        
        if "generate" in start.lower():
            generateImage()
            break
        elif "edit" in start.lower():
            break
            
        else:
            print("Please enter a valid option: 'draw' or 'edit'.")
            continue
        
    editImage()



if __name__ == "__main__":
    roboticArm.reset_position()
    main()