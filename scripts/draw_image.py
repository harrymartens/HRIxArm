from Utils.RoboticPathMovement.robotConfig import RoboticArm

from Utils.UserInput.inputController import receiveInput
from Utils.ImageToVectorConversion.processImage import processImage
from Utils.ImageGeneration.generateImageOpenAI import generate_image_gpt_image_1
from Utils.RoboticPathMovement.moveRobot import executeDrawingCommands

from pyfiglet import Figlet
import cv2


def main():
    f = Figlet(font="slant")
    print(f.renderText("Robot Drawer"))

    arm = RoboticArm()
    arm.intermediate_position()
    arm.reset_position()

    prompt = receiveInput("What would you like to draw?")

    print(f"Generating Image of: {prompt}")
    image_base64 = generate_image_gpt_image_1(prompt)
    contours, lineImage = processImage(image_base64)

    cv2.imshow("Generated Image", lineImage)
    _ = receiveInput("Are you ready to draw? Make sure the pen is attached.")
    
    arm.intermediate_position()
    arm.centre_position()
    executeDrawingCommands(arm, contours, lineImage.shape[:2])
    
    arm.centre_position()
    arm.intermediate_position()
    arm.reset_position()

if __name__ == "__main__":
    main()
