from RoboticPathMovement.robotConfig import RoboticArm

from UserInput.inputController import receiveInput
from ImageToVectorConversion.processImage import processImage
from ImageGeneration.generateImageOpenAI import generate_image_gpt_image_1
from RoboticPathMovement.moveRobot import executeDrawingCommands

from pyfiglet import Figlet
import cv2



def main():
    f = Figlet(font="slant")
    print(f.renderText("Robot Drawer"))
    
    arm = RoboticArm()
    arm.reset_position()
    
    prompt = receiveInput("What would you like to draw?")
    
    print(f"Generating Image of: {prompt}")
    image_base64 = generate_image_gpt_image_1(prompt)
    
    contours, lineImage = processImage(image_base64)
    
    cv2.imshow("Generated Image", lineImage)
    
    arm.centre_position()
    executeDrawingCommands(arm, contours, lineImage.shape[:2])


if __name__ == "__main__":
    main()