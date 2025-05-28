#!/usr/bin/env python3
from pyfiglet import Figlet
import cv2
from PIL import Image
import numpy as np

from UserInput.inputController import receiveInput
from PhotoCapture.photoCapture import capturePhoto

from ImageGeneration.generateImageOpenAI import generateImage, editImage

from ImageToVectorConversion.processImage import processImage

from RoboticPathMovement.robotConfig import RoboticArm
from RoboticPathMovement.moveRobot import executeDrawingCommands




# -------------------------------------------
# User Input
# -------------------------------------------
# Prompt the user for input

# print()
# prompt = receiveInput()


# -------------------------------------------
# Photo Capture
# -------------------------------------------
# Capture a photo of the current drawing
# photo = capturePhoto()

# If the user pressed ESC, exit
# if photo is None:
#     exit(0)


# -------------------------------------------
# Image Generation
# -------------------------------------------

# prompt = "A basic line drawing of a flower in the centre of the screen"
# additional_prompt = "Add a sun and clouds in the sky, and grass in the foreground"

# generatedImage = generateImage(prompt)

# edittedImage = editImage(prompt, additional_prompt, generatedImage)

# -------------------------------------------
# Image to Vector Conversion
# -------------------------------------------


# -------------------------------------------
# Robotic Arm Control
# -------------------------------------------

def showImage(image, title="Result"):
    """
    Display the image using OpenCV.
    """
    pil_img = image.convert("RGB")

    np_img = np.array(pil_img)

    bgr_img = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)

    cv2.imshow(title, bgr_img)
    cv2.waitKey(1)
    cv2.destroyAllWindows()
    
    
    
def editDrawing():
    
    while True:
        
        begin = receiveInput("Let me know when you're ready, and I can add to our drawing. If you've finished, just say 'exit' to leave.")
        
        if "exit" in begin:
            print("Thanks for drawing with me! See you next time!")
            exit(0)
            break
        
        print("\nAwesome! Let me take at look at what you've drawn so far.\n")
        
        # Capture a photo
        photo = capturePhoto()
        if photo is None:
            print("No photo captured. Please try again.")
            continue
        
        additionPrompt = receiveInput("What would you like me to add to your drawing? If you don't know, just say 'random' and I'll think of something.")
        
        existingImage = receiveInput("Could you please describe your existing drawing?")

        if additionPrompt == "random":
            # LLM Random Prompt
            additionPrompt = "A sun in the top right corner of the image"
            
            
        generatedImage = editImage(existingImage,  additionPrompt, photo)
        
        showImage(generatedImage)
        
        while True:
            confirmation = receiveInput("\nWould you like me to draw this? If you don't like it, I can create something different. (yes/no)")
            
            if "yes" in confirmation:
                print("Great! I'll get started.")
                # ---- FIND DIFFERENCE AND DRAW
                print("Drawing the image...")
                # drawImage(generatedImage)
                break
            elif "no" in confirmation:
                
                print("No problem! I'll create something different.")
                prompt = receiveInput("What would you like me to draw?")
                
                generatedImage = editImage(existingImage,  prompt, photo)
                
                showImage(generatedImage)
                
                continue
            
        
        
        
        

def beginDrawing():
    prompt = receiveInput("Is there something specific you would like me to draw? If you're unsure, just say 'random' and I'll think of something.")
    
    if prompt == "random":
        # LLM Random Prompt
        prompt = "A basic line drawing of a flower in the centre of the screen"
        
    generatedImage = generateImage(prompt)
    
    showImage(generatedImage, "Generated Image")
    
    while True:
        confirmation = receiveInput("\nWould you like me to draw this? If you don't like it, I can create something different. (yes/no)")
        
        if "yes" in confirmation:
            print("\nGreat! I'll get started.")
            print("Drawing the image...")
            # drawImage(generatedImage)
            break
        elif "no" in confirmation:
            print("\nNo problem! I'll create something different.")
            prompt = receiveInput("What would you like me to draw?")
            
            generatedImage = generateImage(prompt)
            
            showImage(generatedImage)
            
            continue
        else:
            print("\nSorry, I didn't catch that. Please try again.")
            continue
    
    
    nextStep = receiveInput("\nI've finished my drawing! Would you like to continue drawing, or to exit?")
    
    if "exit" in nextStep:
        print("Thanks for drawing with me! See you next time!")
        exit(0)
    
    editDrawing()
    
    
    

def drawImage(image):
    contours, lineImage = processImage(image)
    roboticArm = RoboticArm()
    executeDrawingCommands(roboticArm, contours)
    

def getInteractionMode():
    
    """
    Greet the user with a welcome message.
    """
    print("Let's get started!")
    while True:
        response = receiveInput("Would you like to start off drawing, or for me to get it started? (me/you)")
        
        if "you" in response:
            print("\nGreat! I'll get started.")
            return "robot"
        elif "me" in response:
            print("\nGreat! You can start drawing.")
            return "user"
        
        print("\nSorry, I didn't catch that. Please try again.")

if __name__ == "__main__":
    f = Figlet(font="slant")
    print(f.renderText("Robot Chat"))
    
    interactionMode = getInteractionMode()
    
    if interactionMode == "robot":
        beginDrawing()
    elif interactionMode == "user":
        editDrawing()


