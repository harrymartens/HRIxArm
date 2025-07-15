import matplotlib.pyplot as plt
from PIL import Image  # or however you obtain your Image objects
import cv2
import numpy as np
from base64 import b64decode, b64encode
from io import BytesIO


def displayImages(img1, img2):
    """
    Show img1 and img2 side by side in a blocking window.
    """
    fig, axes = plt.subplots(1, 2, figsize=(8, 4))
    for ax, img in zip(axes, (img1, img2)):
        ax.imshow(img)
        ax.axis('off')
    plt.tight_layout()
    plt.show()  # blocks until you close the window


def pil_to_mat(pil_img: Image.Image) -> np.ndarray:
    """
    Convert a PIL Image to an OpenCV Mat (numpy.ndarray in BGR order).
    """
    # PIL gives RGB or L; convert to numpy array first
    arr = np.array(pil_img)
    if arr.ndim == 2:
        # grayscale image
        return arr
    # otherwise assume RGB or RGBA
    if arr.shape[2] == 3:
        # RGB → BGR
        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    elif arr.shape[2] == 4:
        # RGBA → BGRA
        return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGRA)
    else:
        raise ValueError(f"Unsupported channel count: {arr.shape[2]}")
    
def mat_to_base64(image, ext=".png"):
    success, buffer = cv2.imencode(ext, image)
    if not success:
        raise ValueError("Image encoding failed")
    return b64encode(buffer).decode("utf-8")

def base64_to_mat(base64_string):
    img_data = b64decode(base64_string)
    np_arr = np.frombuffer(img_data, dtype=np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Decoding failed")
    return image

def base64_to_buffer(base64_image):
    img_bytes = b64decode(base64_image)
    image_buffer = BytesIO(img_bytes)
    image_buffer.name = "image.png"
    return image_buffer

def show_images(*images, titles=None):
    for i, img in enumerate(images):
        title = titles[i] if titles else f"Image {i+1}"
        cv2.imshow(title, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    