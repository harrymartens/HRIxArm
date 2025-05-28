#!/usr/bin/env python3
from pyfiglet import Figlet

from UserInput.inputController import receiveInput
from PhotoCapture.photoCapture import capturePhoto


from ImageToVectorConversion.processImage import processImage


from RoboticPathMovement.robotConfig import RoboticArm
from RoboticPathMovement.moveRobot import executeDrawingCommands



import cv2
from openai import OpenAI
import base64

client = OpenAI()


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")



def generate_image_to_image(original_image, prompt):
    response = client.responses.create(
        model="gpt-4o",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": f"Change the image to reflect the following prompt: {prompt}. Imagine you are an innovative, distinctive artist who applies peoples requests, expanding on them with immense detail to create unique works of art.  Make sure the image is drawable using a marker with a 5mm tip. "},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{original_image}",
                    }
                    ],
            }
        ],
        tools=[{"type": "image_generation"}],
    )
        
    image_data = [
        output.result
        for output in response.output
        if output.type == "image_generation_call"
    ]
        
    if image_data:
        image_base64 = image_data[0]
        with open("genImg.png", "wb") as f:
            f.write(base64.b64decode(image_base64))
        return image_base64, response
    return None, None
    
    
def main():      
    #Capture current drawing
    image_path = "Images/InputImages/horse.png"
    base64_image = encode_image(image_path)
    
    while True:
        #Ask user how the image should be altered
        user_prompt = receiveInput("How would you like to alter your image?")

        #Generate new image based on user prompt
        image_base64, response = generate_image_to_image(base64_image, user_prompt)
        generatedImage = cv2.imread("genImg.png")

        #Process generated image to vector format
        contours, lineImage = processImage(generatedImage)
        
        
        #Display images
        cv2.imshow("Contours", generatedImage)
        cv2.imshow("Line Image", lineImage)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        #Confirm with user if they like the image
        follow_up = input("Would you like to refine this image further? Enter a new prompt or press Enter to continue: ").strip()
        if not follow_up:
            break
        response = client.responses.create(
            model="gpt-4o",
            previous_response_id=response.id,
            input=follow_up,
            tools=[{"type": "image_generation"}],
        )
        image_data = [
            output.result
            for output in response.output
            if output.type == "image_generation_call"
        ]
        if image_data:
            image_base64 = image_data[0]
            with open("genImg.png", "wb") as f:
                f.write(base64.b64decode(image_base64))
            generatedImage = cv2.imread("genImg.png")
            contours, lineImage = processImage(generatedImage)
            cv2.imshow("Contours", generatedImage)
            cv2.imshow("Line Image", lineImage)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    
    #Draw the image
    print("DRAWING")
    # roboticArm.centre_position()
    # executeDrawingCommands(roboticArm, contours, lineImage.shape[:2])
    
    
    


if __name__ == "__main__":
    f = Figlet(font="slant")
    print(f.renderText("Robot Chat"))
    print("\nI am a collaborative drawing robot, interpreting your prompts to creatively transform and enhance your artwork. Watch as our combined vision unfolds on the canvas.\n")

    # roboticArm = RoboticArm()
    # roboticArm.reset_position()
    
    main()
