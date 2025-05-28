#!/usr/bin/env python3
from pyfiglet import Figlet

from UserInput.inputController import receiveInput
from PhotoCapture.photoCapture import capturePhoto

from ImageGeneration.generateImageOpenAI import generateImage, editImage

from ImageToVectorConversion.processImage import processImage

from HelperFunctions.helperFunctions import displayImages

from RoboticPathMovement.robotConfig import RoboticArm
from RoboticPathMovement.moveRobot import executeDrawingCommands, draw_corner_dots


f = Figlet(font="slant")
print(f.renderText("Robot Chat"))

roboticArm = RoboticArm()
roboticArm.reset_position()

canvasSize = roboticArm.get_dimensions()


# roboticArm.centre_position()

# draw_corner_dots(roboticArm)


# roboticArm.calibrate_corners()


while True:



# -------------------------------------------
# User Input
# -------------------------------------------
# Prompt the user for input

    print()
    prompt = receiveInput("What would you like to draw?")


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

    generatedImage = generateImage(prompt)

# edittedImage = editImage(prompt, additional_prompt, generatedImage)

# -------------------------------------------
# Image to Vector Conversion
# -------------------------------------------

    contours, lineImage = processImage(generatedImage, canvasSize)


# -------------------------------------------
# Display Images
# -------------------------------------------
    displayImages(generatedImage, lineImage)

    choice = input("Press Enter to accept, or type 'r' + Enter to regenerate: ").strip().lower()
    if choice != 'r':
        break
    

# -------------------------------------------
# Robotic Arm Control
# -------------------------------------------

roboticArm.centre_position()
executeDrawingCommands(roboticArm, contours, lineImage.shape[:2])





