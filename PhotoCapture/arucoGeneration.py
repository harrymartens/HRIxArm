import cv2
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
for i in range(4):
    img = cv2.aruco.generateImageMarker(aruco_dict, i, 200)
    cv2.imwrite(f'marker_{i}.png', img)