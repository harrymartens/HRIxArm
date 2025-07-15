import cv2
from PIL import Image
import numpy as np


from HelperFunctions.helperFunctions import base64_to_mat, pil_to_mat


def scaleImage(image, target_width=200, target_height=200):
    original_height, original_width = image.shape[:2]
    
    aspect_ratio = original_width / original_height
    
    if original_width > original_height:
        new_width = min(target_width, int(target_height * aspect_ratio))
        new_height = int(new_width / aspect_ratio)
    else:
        new_height = min(target_height, int(target_width / aspect_ratio))
        new_width = int(new_height * aspect_ratio)
    
    resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    return resized_image


def toGrayscale(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray_image

def applyGaussianSmoothing(image, sigma=1):
    smoothed_image = cv2.GaussianBlur(image, (5, 5), sigma)
    return smoothed_image


def cannyLines(img):
    return cv2.Canny(img, 50, 100)

def flipImage(img):
    return cv2.flip(img, 0)


def imagePreprocessingPipeline(image):
    """
    Accepts either a base64 string or a PIL Image and processes it through
    resizing, grayscale conversion, and smoothing.
    """
    if isinstance(image, str):
        # assume base64
        mat_image = base64_to_mat(image)
    elif isinstance(image, Image.Image):
        # assume PIL Image
        mat_image = pil_to_mat(image)
    elif isinstance(image, np.ndarray):
        # already a mat
        mat_image = image
    else:
        raise TypeError(f"Unsupported input type: {type(image)}")

    scaled_image = scaleImage(mat_image, 500, 500)
    gray_image = toGrayscale(scaled_image)
    smoothed_image = applyGaussianSmoothing(gray_image)
    return smoothed_image


def binarize_drawing(image, threshold=128):
    # Convert to grayscale
    gray = toGrayscale(image)

    # Apply Gaussian blur to smooth noise slightly (optional but recommended)
    blurred = applyGaussianSmoothing(gray)

    # Binarize using thresholding
    _, binarized = cv2.threshold(blurred, threshold, 255, cv2.THRESH_BINARY)
    cv2.imshow("Bin", binarized)
    cv2.waitKey(0)

    return binarized