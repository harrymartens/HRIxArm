from base64 import b64decode
from io import BytesIO

from PIL import Image
import cv2
import numpy as np
from alive_progress import alive_bar
from openai import OpenAI

client = OpenAI()

def generateImageOpenAI(prompt):
    """
    Generates an image using a given prompt and returns it as a PIL Image object.
    """
    
    prompt = prompt + ". Ensure the image is a minimalistic, high-contrast black and white line drawing of only the specified subject on a plain white background, with bold, clear outlines and no additional details."

    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        quality="low",
        size="1024x1536",
    )

    image_base64 = result.data[0].b64_json
    image_bytes = b64decode(image_base64)
    image = Image.open(BytesIO(image_bytes))

    return image


def editImageOpenAI(prompt, additional_prompt, image):
    """
    Generates a mask and uses it to edit an image based on a secondary prompt.
    """
    # Generate mask

    prompt_mask = (
        f"Generate a black and white binary mask. The black area should be a suitable region for '{additional_prompt}'. "
        "The white area should be covering all other existing objects in the image, which should remain unchanged.. "
        "Ensure the mask is the same size as the input image."
    )
    
    # 1. Convert to RGB channel order
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # 2. Create a PIL Image
    pil_img = Image.fromarray(rgb)   # now mode="RGB"
    
    pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)).resize((600, 600), Image.LANCZOS)

    # Convert input image to bytes for API call
    buffered = BytesIO()
    pil_img.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    img_buffer = BytesIO(img_bytes)
    img_buffer.name = "image.png"

    result_mask = client.images.edit(
        model="gpt-image-1",
        image=img_buffer,
        prompt=prompt_mask,
        size="1536x1024"

    )

    image_base64 = result_mask.data[0].b64_json
    image_bytes = b64decode(image_base64)
    
    
    mask_image = Image.open(BytesIO(image_bytes)).resize((600, 600), Image.LANCZOS)
    

    # Convert mask to have alpha channel
    mask_rgba = mask_image.convert("L").convert("RGBA")
    mask_rgba.putalpha(mask_image.convert("L"))

    # Convert mask_rgba to bytes for API call
    buffered_mask = BytesIO()
    mask_rgba.save(buffered_mask, format="PNG")
    mask_bytes = buffered_mask.getvalue()
    mask_buffer = BytesIO(mask_bytes)
    mask_buffer.name = "mask.png"
    
    full_prompt = f"{prompt}, {additional_prompt}. Maintain the original style and placement of the existing elements in the image. Insert the additional element without moving any other objects."

    result_mask_edit = client.images.edit(
        model="gpt-image-1",
        prompt=full_prompt,
        image=img_buffer,
        mask=mask_buffer,
        size="1536x1024"
    )

    image_base64 = result_mask_edit.data[0].b64_json
    image_bytes = b64decode(image_base64)
    edited_image = Image.open(BytesIO(image_bytes))

    return edited_image, mask_rgba


def generateImage(prompt):
    """
    Generates an image based on a prompt, displays it, and returns it.
    """
    with alive_bar(1, title="Generating Image", spinner="dots_waves") as bar:
        image = generateImageOpenAI(prompt)
        bar()
    return image


def editImage(original_prompt, additional_prompt, image):
    """
    Edits an image by adding new content based on an additional prompt,
    displays the original image, the generated mask, and the edited image,
    and returns the edited image.
    """
    with alive_bar(1, title="Editing Image", spinner="dots_waves") as bar:
        edited_img, mask_rgba = editImageOpenAI(original_prompt, additional_prompt, image)
        bar()

    return edited_img