import cv2
import numpy as np

# ─── 1. LOAD IMAGES ───────────────────────────────────────────────────────────
# Replace these paths with your actual file names (or full paths).
imgA_path = "Images/inputImages/originalDrawing.jpg"  # “bird alone”
imgB_path = "Images/inputImages/.jpg"  # “bird with tophat”

imageA = cv2.imread(imgA_path)
imageB = cv2.imread(imgB_path)

if imageA is None or imageB is None:
    raise FileNotFoundError("One of the input images was not found. Check your paths.")

# Make copies for visualization later
origA = imageA.copy()
origB = imageB.copy()

# ─── 2. CONVERT TO GRAYSCALE AND BLUR ───────────────────────────────────────────
# We blur slightly to reduce noise in keypoint matching and in the difference step.
grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)
grayA = cv2.GaussianBlur(grayA, (5, 5), 0)
grayB = cv2.GaussianBlur(grayB, (5, 5), 0)

# ─── 3. DETECT AND DESCRIBE KEYPOINTS WITH ORB ─────────────────────────────────
# ORB is free to use and relatively fast. We detect up to 5000 keypoints in each image.
orb = cv2.ORB_create(5000)
kpsA, descA = orb.detectAndCompute(grayA, None)
kpsB, descB = orb.detectAndCompute(grayB, None)

# ─── 4. MATCH DESCRIPTORS USING BFMatcher ──────────────────────────────────────
# Since ORB uses a binary descriptor, we use Hamming distance.
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
matches = bf.match(descA, descB)
# Sort matches by distance (i.e. quality of match)
matches = sorted(matches, key=lambda x: x.distance)
# Keep only the top N matches (e.g. top 100) to reduce outliers
num_good_matches = 100
good_matches = matches[:num_good_matches]

# (Optional) Visualize the matches—uncomment if you want to see them.
# matched_vis = cv2.drawMatches(grayA, kpsA, grayB, kpsB, good_matches, None, flags=2)
# cv2.imwrite("matches.png", matched_vis)

# ─── 5. COMPUTE HOMOGRAPHY VIA RANSAC ───────────────────────────────────────────
# We need ≥4 matched points to compute a homography. Build two coordinate arrays.
if len(good_matches) < 4:
    raise RuntimeError("Not enough matches to compute homography (need >= 4).")

# Extract matched keypoint coordinates
ptsA = np.float32([kpsA[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
ptsB = np.float32([kpsB[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

# Solve for H such that:  ptsA ≈ H · ptsB
H, status = cv2.findHomography(ptsB, ptsA, cv2.RANSAC, 5.0)

if H is None:
    raise RuntimeError("Homography computation failed.")

# ─── 6. WARP IMAGE B ONTO IMAGE A’S FRAME ───────────────────────────────────────
heightA, widthA = imageA.shape[:2]
alignedB = cv2.warpPerspective(imageB, H, (widthA, heightA))

# ─── 7. COMPUTE PIXEL-WISE DIFFERENCE ───────────────────────────────────────────
# Convert the warped image to grayscale and blur once more (for cleaner diff)
grayAlignedB = cv2.cvtColor(alignedB, cv2.COLOR_BGR2GRAY)
grayAlignedB = cv2.GaussianBlur(grayAlignedB, (5, 5), 0)

# Absolute difference between warped B and A
diff = cv2.absdiff(grayAlignedB, grayA)

# ─── 8. BINARY THRESHOLD TO ISOLATE CHANGED REGION ─────────────────────────────
# Any pixel difference > 30 (tuned for this example) is considered “changed”
_, mask = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

# ─── 9. MORPHOLOGICAL CLEANUP ───────────────────────────────────────────────────
# Remove small speckles and fill small holes so that the tophat is one solid blob
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  # fill interior gaps
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)   # remove small noise

# ─── 10. FIND LARGEST CONTOUR (ASSUMING Tophat IS THE BIGGEST CHANGE) ─────────
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
if len(contours) == 0:
    raise RuntimeError("No contours found in difference mask—maybe adjust threshold or alignment.")

# Pick contour with max area
largest_contour = max(contours, key=cv2.contourArea)
x, y, w, h = cv2.boundingRect(largest_contour)

# ─── 11. EXTRACT OR OVERLAY THE REGION ───────────────────────────────────────────
# 11a. Create a colored overlay on top of Image A to show where the tophat is
overlay = origA.copy()
cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 255, 0), 2)  # green box

# 11b. Optionally extract the hat alone as a transparent PNG
#      We’ll crop from alignedB (bird+hat) using the bounding‐box, then apply the mask as alpha.
cropped_hat = alignedB[y : y + h, x : x + w]
cropped_mask = mask[y : y + h, x : x + w]

# Create an RGBA image where mask=255 → opaque, mask=0 → transparent
b_chan, g_chan, r_chan = cv2.split(cropped_hat)
alpha_chan = cropped_mask  # white = hat, black = background
rgba_hat = cv2.merge([b_chan, g_chan, r_chan, alpha_chan])

# ─── 12. SAVE OR SHOW RESULTS ───────────────────────────────────────────────────
# Save the binary difference mask
cv2.imwrite("difference_mask.png", mask)

# Save the overlay (Image A with bounding box around “changed” region)
cv2.imwrite("hat_bbox_overlay.png", overlay)

# Save the extracted tophat (RGBA PNG). “hat_cutout.png” will have transparent background.
cv2.imwrite("hat_cutout.png", rgba_hat)

# (Optional) display intermediate windows—uncomment if you want to visualize
# cv2.imshow("Aligned B", alignedB)
# cv2.imshow("Absolute Difference", diff)
# cv2.imshow("Binary Mask", mask)
# cv2.imshow("Bounding Box Overlay", overlay)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

print("All steps complete. Outputs written:")
print(" • difference_mask.png       (binary mask of changed pixels)")
print(" • hat_bbox_overlay.png      (Image A with bounding box around tophat)")
print(" • hat_cutout.png            (RGBA PNG of just the tophat)")

