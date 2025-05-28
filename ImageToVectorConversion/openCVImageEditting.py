import cv2

from HelperFunctions.helperFunctions import pil_to_mat


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
    
    mat_image = pil_to_mat(image)
    
    scaled_image = scaleImage(mat_image, 500, 500)
    gray_image = toGrayscale(scaled_image)
    smoothed_image = applyGaussianSmoothing(gray_image)
    return smoothed_image