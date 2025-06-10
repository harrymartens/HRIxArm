from photoCapture import capturePhoto
from HRIxArm.PhotoCapture.identifyMarkers import scanImageAndCrop
import cv2

image = capturePhoto()

cropped_image = scanImageAndCrop(image)