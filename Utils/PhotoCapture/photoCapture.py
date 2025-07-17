import cv2


def capturePhoto():
    """
    Opens the webcam, captures one frame when you press SPACE,
    and saves it to disk.
    """
    
    camera_index=0
    
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return None

    print("📷 Camera opened. Press SPACE to capture, ESC to cancel.")
    frame = None

    while True:
        ret, img = cap.read()
        if not ret:
            print("❌ Failed to grab frame")
            break

        cv2.imshow("Press SPACE to capture, ESC to cancel", img)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:           # ESC
            print("\n🚪 Capture cancelled. Exiting without saving.\n")
            break
        elif key == 32:         # SPACE
            frame = img.copy()
            print("\n✅ Image captured.\n")
            break

    cap.release()
    cv2.destroyAllWindows()
    
    return frame


