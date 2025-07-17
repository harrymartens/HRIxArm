import cv2
import time
from datetime import datetime
from pathlib import Path

def capturePhoto(
    camera_index: int = 0,
    warmup: float = 1.0,
    save: bool = True,
    out_dir: str = "captured"
):
    """
    Automatically captures a single photo from the webcam.

    Parameters
    ----------
    camera_index : int
        Index of the camera to open (default 0).
    warmup : float
        Seconds to wait (and discard frames) so the camera can auto-expose.
    save : bool
        If True, save the image to disk.
    out_dir : str
        Directory to save the image if `save` is True.

    Returns
    -------
    frame : numpy.ndarray | None
        The captured image or None if capture failed.
    """

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return None

    print(f"📷 Camera opened. Warming up for {warmup:.1f}s …")
    start = time.time()
    while time.time() - start < warmup:
        cap.read()                       # throwaway frames during warm-up

    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("❌ Failed to grab frame")
        return None

    if save:
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        filename = Path(out_dir) / f"photo_{datetime.now():%Y%m%d_%H%M%S}.jpg"
        cv2.imwrite(str(filename), frame)
        print(f"✅ Image captured and saved to {filename}")
    else:
        print("✅ Image captured (not saved)")

    return frame
