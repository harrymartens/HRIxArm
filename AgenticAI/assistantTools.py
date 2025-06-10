import cv2

from ImageGeneration.generateImageOpenAI import edit_image_gpt_image_1, generate_image_gpt_image_1, image_description
from HelperFunctions.helperFunctions import base64_to_mat, mat_to_base64, show_images, base64_to_buffer
from ImageToVectorConversion.processImage import processImage
from UserInput.inputController import receiveInput
from RoboticPathMovement.moveRobot import draw_contours
from PhotoCapture.photoCapture import capturePhoto
from PhotoCapture.identifyMarkers import scanImageAndCrop




def generate_drawing(prompt, roboticArm):
    # return f"The drawing of {prompt} has been complete"
    
    image_base64 = generate_image_gpt_image_1(prompt)
        
    generated_image = base64_to_mat(image_base64)
        
    contours, lineImage = processImage(generated_image)
        
    show_images(generated_image, lineImage, titles=["Generated Image", "Contours"])
    
    confirmation = receiveInput("Would you like me to draw this image? (yes/no)")
    
    if "no" in confirmation.strip().lower():
        return f"The user rejected the generated image before it could be drawn: '{prompt}'."

    draw_contours(roboticArm, contours, lineImage.shape[:2])
    return f"The drawing of {prompt} has been complete"
    
    
def edit_drawing(prompt, roboticArm):
    # return f"The drawing of {prompt} has been complete"
    current_image = capturePhoto()
    if current_image is None:
        return "Capture of existing drawing failed unexpectedly."
    cropped_image = scanImageAndCrop(current_image)
        
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

    draw_contours(roboticArm, contours, lineImage.shape[:2])
    return f"The drawing of {prompt} has been complete"
    
def capture_image():
    # return "the drawing is of a cow wearing a tutu"
    
    
    current_image = capturePhoto()
    if current_image is None:
        return "Capture of existing drawing failed unexpectedly."
    cropped_image = scanImageAndCrop(current_image)
        
    flipped_image = cv2.flip(cropped_image, -1)
    
    base64_image = mat_to_base64(flipped_image)
    
    return image_description(base64_image)
    
def draw_image(img, prompt, roboticArm):
    
    if img == None:
        return "No Images have been generated yet"
    
    contours, lineImage = processImage(img)
    
    draw_contours(roboticArm, contours, lineImage.shape[:2])
    return f"The drawing of {prompt} has been complete"