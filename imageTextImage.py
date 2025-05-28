#!/usr/bin/env python3
from pyfiglet import Figlet

from UserInput.inputController import receiveInput
from PhotoCapture.photoCapture import capturePhoto

from ImageGeneration.generateImageOpenAI import generateImage, editImage

from ImageToVectorConversion.processImage import processImage

from HelperFunctions.helperFunctions import displayImages

from RoboticPathMovement.robotConfig import RoboticArm
from RoboticPathMovement.moveRobot import executeDrawingCommands, draw_corner_dots


# f = Figlet(font="slant")
# print(f.renderText("Robot Chat"))

# roboticArm = RoboticArm()
# roboticArm.reset_position()

# canvasSize = roboticArm.get_dimensions()
import cv2
from openai import OpenAI
import base64

client = OpenAI()



def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


image_path = "Images/InputImages/horse.png"

base64_image = encode_image(image_path)


response = client.responses.create(
    model="gpt-4.1",
    input=[
        {
            "role": "user",
            "content": [
                { "type": "input_text", "text": "Desribe the object in the drawing. Describe the placement of all details in detail. Exclude any infomation of style. " },
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{base64_image}",
                },
            ],
        }
    ],
)



print(response.output_text)

analysis = response.output_text

    
response = client.responses.create(
    model="gpt-4.1-mini",
    input =
    "Restyle the provided image in an abstract artistic style" +
    "Ensure the image has high contrast lines" + 
    "Only include the specified object(s); do not add backgrounds, borders, or extra elements: " + analysis,
    tools=[{"type": "image_generation"}],
)
    
image_data = [
    output.result
    for output in response.output
    if output.type == "image_generation_call"
]
    
if image_data:
    image_base64 = image_data[0]
    with open("bug.png", "wb") as f:
        f.write(base64.b64decode(image_base64))
        
        
generatedImage = cv2.imread("bug.png")
contours, lineImage = processImage(generatedImage)

displayImages(generatedImage, lineImage)

        

    
# Scan Existing Drawing

# Interpret drawing to text

# Draw the text in alternate style

# OR

# Scan the existing drawing

# Interpret and suggest Addition

# Draw with addition



# -------------------------------------------
# User Input
# -------------------------------------------
# Prompt the user for input

    # prompt = receiveInput("What would you like to draw?")


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

    # contours, lineImage = processImage(generatedImage, canvasSize)


# -------------------------------------------
# Display Images
# -------------------------------------------
    # displayImages(generatedImage, lineImage)

    # choice = input("Press Enter to accept, or type 'r' + Enter to regenerate: ").strip().lower()
    # if choice != 'r':
    #     break
    

# -------------------------------------------
# Robotic Arm Control
# -------------------------------------------

# roboticArm.centre_position()
# executeDrawingCommands(roboticArm, contours, lineImage.shape[:2])





