import matplotlib.pyplot as plt
from PIL import Image  # or however you obtain your Image objects
import cv2
import numpy as np

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