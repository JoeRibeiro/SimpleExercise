# import the necessary packages
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
from os import walk

def midpoint(ptA, ptB):
	return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

# Set the path to the image folder
image_folder = r'C:\Users\JR13\OneDrive - CEFAS\My onedrive documents\SimpleExercise\data\raw\\'

# Display a message with the image folder location
print("Hi! An image window should pop up. Press any key to cycle through images. Please set the image folder location in planktonsize.py. We will be looking in: " + image_folder)

# Get the list of filenames in the specified folder
filenames = next(walk(image_folder), (None, None, []))[2]

# Initialize lists to store plankton lengths and corresponding file names
plengths = []
fnames = []

# Flag to indicate whether to use brute force method for alternative distance calculation
brute_force = False

# Iterate through each image file in the folder
for filename in [image_folder + myname for myname in filenames]:
    # Load the image and convert it to grayscale
    image = cv2.imread(filename)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Perform edge detection, followed by dilation and erosion to close gaps
    edged = cv2.Canny(gray, 30, 100)  # 30 on the Canny picks up fine edges on copepods
    edged = cv2.dilate(edged, None, iterations=1)
    edged = cv2.erode(edged, None, iterations=1)

    # Find contours in the edge map
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    # Sort contours from left-to-right and initialize the 'pixels per metric' calibration variable
    (cnts, _) = contours.sort_contours(cnts)

    # Identify the contour of the plankton (largest contour)
    c = max(cnts, key=cv2.contourArea)

    # Compute the rotated bounding box of the contour
    orig = image.copy()
    box = cv2.minAreaRect(c)
    box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
    box = np.array(box, dtype="int")

    # Order the points in the contour to appear in top-left, top-right, bottom-right, and bottom-left order
    box = perspective.order_points(box)

    # Draw the outline of the rotated bounding box and original points
    cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

    # Loop over the original points and draw them
    for (x, y) in box:
        cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)

    # Compute midpoints between different pairs of bounding box points
    (tl, tr, br, bl) = box
    (tltrX, tltrY) = midpoint(tl, tr)
    (blbrX, blbrY) = midpoint(bl, br)
    (tlblX, tlblY) = midpoint(tl, bl)
    (trbrX, trbrY) = midpoint(tr, br)

    # Draw lines between midpoints
    cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)), (255, 0, 255), 2)
    cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)), (255, 0, 255), 2)

    # Compute Euclidean distances between midpoints
    dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
    dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

    # Calculate an alternative distance using a brute force method if specified
    alternative_distance = min(dA, dB)
    if brute_force:
        for acoords in c:
            for bcoords in c:
                dc = abs(dist.euclidean((acoords[0][0], acoords[0][1]), (bcoords[0][0], bcoords[0][1])))
                if dc > alternative_distance:
                    alternative_distance = dc
        print(alternative_distance)
    fnames.append(filename)
    plengths.append(round(alternative_distance))

    # Display the output image with length information
    cv2.imshow("length in pixels is between " + str(int(max(dA, dB))) + " and " + str(int(alternative_distance)) + " pixels", orig)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


result = np.array([fnames,plengths])
np.savetxt("plankton_lengths.csv", result[result[:,1].argsort()], delimiter=",", header='string', comments='', fmt='%s')

