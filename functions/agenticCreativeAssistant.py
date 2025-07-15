from openai import OpenAI
import json
from pyfiglet import Figlet

client = OpenAI()

from RoboticPathMovement.robotConfig import RoboticArm

from AgenticTools.assistantTools import generate_drawing, edit_drawing, capture_image, draw_image

from UserInput.inputController import receiveInput

roboticArm = RoboticArm()

assistant = client.beta.assistants.create(
  name="Creative Drawing Robot",
    model="gpt-4o",
  instructions="""
    As a creative robotic assistant, you have a 6-axis arm and are equipped with a marker. Your role is to work collaboratively with human artists by assisting in artistic creation and encouraging creativity. This involves brainstorming novel artistic ideas, generating new images to draw, and editing existing images to illustrate new edits.
    Your only purpose is as a creative assistant. You should not provide assistance to questions which dont relate to assisting the users creative and drawing process.

    # Tasks

    1. **Workshopping Ideas**:
    - Engage with the user to explore creative concepts.
    - Ask probing questions to refine and expand on these concepts.

    2. **Generating Images**:
    - Create novel images based on discussed concepts.
    - Ensure the generated images align with the user's desired style and theme.

    3. **Editing Images**:
    - Make precise edits and stylistic changes to existing images already drawn on the canvas as per user feedback.

    # Output Format

    Responses should be structured to guide through idea generation, image creation, and execution of drawing or editing. Offer clear, actionable suggestions and anticipate user queries.
    The robot draws using a single coloured chalk marker on an acrylic sheet. It is limited to a single colour and details available using a 5mm marker.

    # Personality
    
    Act as a kind, charming and helpful artistic assistant.
    
    # Tools
    
    The following tools are avaliable to you:
        generate_image(user_prompt):
            Generates an image using openAI's image API, before decomposing it into line vectors and draws it on the canvas using the robotic arm.
            It is intended to only be used when the canvas is blank, and no previous images have been successfully drawn.
        
        edit_image(user_prompt):
            Captures a photo of the current state of the canvas, before passing the image, along with the user's prompt to the openAI image editting API.
            This generates a new version of the existing artwork, based on the user prompt. It then erases the existing drawing and draws the new version on the canvas.
            
        capture drawing:
            Captures a photo of the current state of the canvas, and returns a description of what is depicted.
    

    # Examples

    - **Example 1: Workshopping Ideas**
    - User Input: "I'm thinking of a futuristic cityscape."
    - Assistant Response: "Let's explore what makes a futuristic cityscape unique. Should we focus on architectural innovations or a particular atmosphere? What graphic style are you considering?"

    - **Example 2: Generating Images**
    - User Input: "Could you create a concept sketch of this cityscape?"
    - Assistant Response: "[Generating concept sketch]. Based on our discussion, here's an initial sketch of the cityscape focusing on towering structures and neon lighting. How does this align with your vision?"

    - **Example 3: Drawing and Editing**
    - User Input: "Add more detail to the skyline."
    - Assistant Response: "[Executing changes]. I've added intricate details to the skyline, emphasizing a mix of historical and modern architecture. Does this enhance the scene as you imagined?"

    # Notes

    - Always check in with the user for feedback on generated outputs.
    - If unsure on the current state of the canvas, call the capture_drawing tool to confirm what is currently drawn.
    - Maintain a flexible approach to accommodate evolving user preferences and ideas.
  """,
  tools=[
    {
        "type": "function",
        "function": {
            "name": "generate_image",
            "description": "Creates an image based on a user-provided prompt and draws it on a canvas, returning a completion message.",
            "strict": True,
            "parameters": {
                "type": "object",
                "required": [
                "image_prompt"
                ],
                "properties": {
                "image_prompt": {
                    "type": "string",
                    "description": "A descriptive prompt to generate the image"
                }
                },
                "additionalProperties": False
            }
        }
    },
    
    {
        "type":"function",
        "function":{
            "name": "edit_image",
            "description": "Edits an existing image already drawn on the canvas based on the user provided prompt.",
            "strict": True,
            "parameters": {
                "type": "object",
                "required": [
                "edit_prompt"
                ],
                "properties": {
                "edit_prompt": {
                    "type": "string",
                    "description": "A descriptive prompt describing how the existing image should be changed"
                }
                },
                "additionalProperties": False
            }
        }
    },
    {
        "type":"function",
        "function": {
            
            "name": "capture_drawing",
            "description": "Captures an image of the current drawing and returns a description of what it is.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
                "required": []
            }
            
        }
    },
    {
        "type":"function",
        "function": {
            
            "name": "draw_last_generated_image",
            "description": "Draws the most recently generated image.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
                "required": []
            }
            
        }
    }
    
    ],
)

def generate_image(prompt: str) -> str:
    
    print("\nGENERARTING IMAGE...\n")
    
    return generate_drawing(prompt, roboticArm)


def edit_image(edit_prompt: str) -> str:
   
    print("\EDITTING IMAGE...\n")

    return edit_drawing(edit_prompt, roboticArm)


def capture_drawing() -> str:
   
    print("\CAPTURING PHOTO...\n")

    return capture_image()


def main():    
    thread = client.beta.threads.create()
    print("Hello—I’m your creative robotic assistant with a 6-axis arm and a single-colour chalk marker.")
    print("I can brainstorm ideas, sketch concepts, or edit your images. What artistic idea would you like to explore today?")
       
    try:
        while True:
            # 3) Get the next user input
            prompt = receiveInput("You: ")

            # 4) Create a user message in the thread
            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=prompt,
            )

            # 5) Let the assistant generate a response (and possibly request a tool call)
            run = client.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id=assistant.id,
                instructions="""
                -Whenever the user indicates for you to view something, call the 'capture_drawing' function.
                -Do not ask the user for a file upload or URL.
                -Keep responses to less than 100 words.
                -Your only purpose is as a creative assistant. You should not provide assistance 
                 to questions which don’t relate to assisting the user’s creative and drawing process.
                """
            )

            # 6) If the assistant asked for one or more tool calls, collect string‐only outputs:
            if run.required_action and run.required_action.submit_tool_outputs:
                tool_outputs = []
                for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                    fn_name = tool_call.function.name
                    # The arguments come in as a JSON‐string
                    args = json.loads(tool_call.function.arguments or "{}")

                    if fn_name == "generate_image":
                        user_prompt = args.get("image_prompt", "")
                        
                        most_recent_prompt = user_prompt
                        
                        result = generate_image(user_prompt)
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": result
                        })

                    elif fn_name == "edit_image":
                        edit_prompt = args.get("edit_prompt", "")
                        
                        most_recent_prompt = edit_prompt

                        result = edit_image(edit_prompt)
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": result
                        })

                    elif fn_name == "capture_drawing":
                        result = capture_drawing()
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": result
                        })
                        

                # 5) Submit the real outputs back to the assistant
                run = client.beta.threads.runs.submit_tool_outputs_and_poll(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )


            # 8) At this point, the assistant has a “final” message. Retrieve and print it:
            if run.status == "completed":
                messages = client.beta.threads.messages.list(thread_id=thread.id)
                # The very last Message in messages.data is the assistant’s final reply
                last_msg = messages.data[0]
                reply = "".join(block.text.value for block in last_msg.content)
                print(f"\nRobot:\n{reply}\n")
            else:
                print(f"Robot status: {run.status}\n")

    except KeyboardInterrupt:
        print("\nConversation ended. Goodbye!")
    
    
    

if __name__ == "__main__":
    f = Figlet(font="slant")
    print(f.renderText("Robot Creative Assistant"))
    main()