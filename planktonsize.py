# import the necessary packages
from scipy.spatial import distance as dist
import numpy as np
import cv2
import imutils
from imutils import contours
from itertools import combinations
import sys
from os import walk, path

def midpoint(ptA, ptB):
    return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

def analyze_plankton(image_folder):
    # Get the list of filenames in the specified folder
    try:
        filenames = next(walk(image_folder), (None, None, []))[2]
    except StopIteration:
        print(f"Error: No files found in the specified folder: {image_folder}")
        sys.exit(1)

    # Initialize lists to store plankton lengths and corresponding file names
    plengths = []
    fnames = []

    # Iterate through each image file in the folder
    for filename in [path.join(image_folder, myname) for myname in filenames]:
        print(f"Processing image: {filename}")

        # Load the image and check if it's loaded successfully
        try:
            image = cv2.imread(filename)
            if image is None:
                print(f"Error: Unable to load image: {filename}")
                continue  # Skip to the next image if loading fails
        except Exception as e:
            print(f"Error: {e}")
            continue  # Skip to the next image in case of an exception

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Perform edge detection, followed by dilation and erosion to close gaps
        edged = cv2.Canny(gray, 30, 100)  # 30 on the Canny picks up fine edges on copepods
        edged = cv2.dilate(edged, None, iterations=1)
        edged = cv2.erode(edged, None, iterations=1)

        # Find contours in the edge map
        cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        # Sort contours from left-to-right
        (cnts, _) = contours.sort_contours(cnts)

        # Identify the contour of the plankton (largest contour)
        if not cnts:
            print(f"Warning: No contours found in image: {filename}")
            continue  # Skip to the next image if no contours are found

        c = max(cnts, key=cv2.contourArea)

        # Calculate distance using convex hull of the contour. This finds the two furthest points by comparing all combinations of points
        objectlength = 0
        c = cv2.convexHull(c)
        for acoords, bcoords in combinations(c, 2):
            # Compute Euclidean distances between points
            dc = abs(dist.euclidean((acoords[0][0], acoords[0][1]), (bcoords[0][0], bcoords[0][1])))
            if dc > objectlength:
                objectlength = dc

        print(f"Plankton length: {objectlength}")

        # Save file name and length to a list
        fnames.append(filename)
        plengths.append(round(objectlength))

    if not fnames:
        print("No valid images found. Exiting.")
        sys.exit(1)

    result = np.array([fnames, plengths]).T
    np.savetxt("plankton_lengths.csv", result[result[:, 1].astype(np.int).argsort()], delimiter=",", comments='', fmt='%s')

if __name__ == "__main__":
    # Check if the correct number of command-line arguments is provided
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <image_folder_path>")
        sys.exit(1)

    # Get the image folder path from the command line
    image_folder_path = sys.argv[1]

    # Call the function to analyze plankton
    analyze_plankton(image_folder_path)
