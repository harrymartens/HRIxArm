from base64 import b64decode
from openai import OpenAI

from pathlib import Path
import base64
import re
from yaspin import yaspin

client = OpenAI()

def slugify(text: str, max_len: int = 64) -> str:
    """
    Turns an arbitrary prompt into a filesystem-friendly slug.
    Keeps letters, numbers, hyphens and underscores; converts spaces to underscores.
    """
    text = text.strip().lower()
    # Replace spaces with underscores
    text = text.replace(" ", "_")
    # Drop anything that isn't alnum, underscore or hyphen
    text = re.sub(r"[^a-z0-9_\-]", "", text)
    return text[:max_len] or "image"

def save_generated_image(b64_data: str, prompt: str, root_dir: str | Path = ".") -> Path:
    """
    Decodes `b64_data`, creates <root_dir>/<prompt>/image.png and returns the path.
    """

    prompt_dir = Path(root_dir) / "Images/GeneratedImages" / slugify(prompt)
    prompt_dir.mkdir(parents=True, exist_ok=True)

    img_path = prompt_dir / "image.png"
    img_bytes = base64.b64decode(b64_data)

    with img_path.open("wb") as f:
        f.write(img_bytes)
        
        

def generate_image_gpt_image_1(prompt: str):
    """
    Generates an image with the gpt-image-1 model and saves it.
    Returns the generated image in base64 format.
    """
    with yaspin(text="Generating image", color="cyan") as spinner:
        try:
            result = client.images.generate(
                model="gpt-image-1",
                prompt=prompt + """
                Generate clean black and moderately simple line art with some details. Use single-pixel wide strokes.
                """,
                quality="medium",
                size="1024x1536",
            )

            image_base64 = result.data[0].b64_json
            saved_path = save_generated_image(image_base64, prompt)

            spinner.ok("✅ ")
            print(f"Image saved to {saved_path}")
            return image_base64

        except Exception as e:
            spinner.fail("💥 ")
            raise


def edit_image_gpt_image_1(original_image, prompt: str, mask=None):
    """
    Edits an image with the gpt-image-1 model.
    If `mask` is supplied, it’s used to constrain the edit.
    Returns the edited image in base64 format.
    """
    with yaspin(text="Editing image", color="cyan") as spinner:
        try:
            if mask:
                response = client.images.edit(
                    model="gpt-image-1",
                    image=original_image,
                    mask=mask,
                    prompt=prompt,
                    size="1024x1536",
                )
            else:
                response = client.images.edit(
                    model="gpt-image-1",
                    image=original_image,
                    prompt=prompt + (
                        "Generate clean black and moderately simple line art with some details. Use single-pixel wide strokes."
                    ),
                    size="1024x1536",
                )

            image_base64 = response.data[0].b64_json
            saved_path = save_generated_image(image_base64, prompt)

            spinner.ok("✅ ")
            print(f"Image saved to {saved_path}")
            return image_base64

        except Exception as e:
            spinner.fail("💥 ")  # red cross on failure
            raise



def image_description(base64_image):
    
    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {
                "role": "user",
                "content": [
                    { "type": "input_text", "text": "Desribe the object in the drawing in 50 words or less." },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            }
        ],
    )
    return response.output_text