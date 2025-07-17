from .openCVImageEditting import imagePreprocessingPipeline, cannyLines, flipImage
from .generateLineSegments import findConnectedComponents



def processImage(image):
    """
    Process the image to convert it into a vector format.
    """
    
    #Scale Down the image, convert to grayscale, and apply Gaussian smoothing
    # to reduce noise and improve edge detection.
    preprocessed_image = imagePreprocessingPipeline(image)
    
    # Apply Canny edge detection to find edges in the image.
    cannyImage = cannyLines(preprocessed_image)
    
    # Flip the image to match the drawing direction of the robotic arm.
    flippedImage = flipImage(cannyImage)
    
    # Connect lines in the image to form contours.
    countours, lineImage = findConnectedComponents(flippedImage)
    
    flippedLineImage = flipImage(lineImage)
    
    return countours, flippedLineImage