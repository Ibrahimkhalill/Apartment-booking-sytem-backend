import cv2
import numpy as np
import requests
import os
import logging

logger = logging.getLogger(__name__)
# Function to measure the foot size using a reference object from a URL
# Function to measure the foot size using a reference object from a URL
def measure_foot(foot_image_path, reference_image_url, known_reference_size):
    # Ensure known_reference_size is a float or int
    known_reference_size = float(known_reference_size)

    # Check if the foot_image_path is a valid file path or an image array
    if isinstance(foot_image_path, str):
        # Load the foot image from the provided file path
        if not os.path.exists(foot_image_path):
            raise ValueError(f"Foot image does not exist at path: {foot_image_path}")
        foot_image = cv2.imread(foot_image_path)
        if foot_image is None:
            raise ValueError("Foot image could not be loaded. Check the file path.")
    elif isinstance(foot_image_path, np.ndarray):
        # If it's an array, use it directly
        foot_image = foot_image_path
    else:
        raise ValueError("Invalid foot image input. Must be a file path or image array.")

    # Proceed with image processing
    gray_foot = cv2.cvtColor(foot_image, cv2.COLOR_BGR2GRAY)
    blurred_foot = cv2.GaussianBlur(gray_foot, (5, 5), 0)
    _, thresholded_foot = cv2.threshold(blurred_foot, 50, 255, cv2.THRESH_BINARY_INV)

    # Find contours of the foot
    contours_foot, _ = cv2.findContours(thresholded_foot, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Load the reference image from the URL
    response = requests.get(reference_image_url)
    if response.status_code != 200:
        raise ValueError(f"Reference image could not be loaded from URL: {reference_image_url}")

    # Convert the image data from the URL to a numpy array
    reference_image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
    reference_image = cv2.imdecode(reference_image_array, cv2.IMREAD_COLOR)
    if reference_image is None:
        raise ValueError("Reference image could not be decoded from the URL.")

    gray_reference = cv2.cvtColor(reference_image, cv2.COLOR_BGR2GRAY)
    blurred_reference = cv2.GaussianBlur(gray_reference, (5, 5), 0)
    _, thresholded_reference = cv2.threshold(blurred_reference, 50, 255, cv2.THRESH_BINARY_INV)

    # Find contours of the reference object
    contours_reference, _ = cv2.findContours(thresholded_reference, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours_foot and contours_reference:
        # Assuming the largest contour is the foot
        largest_contour_foot = max(contours_foot, key=cv2.contourArea)
        x_foot, y_foot, w_foot, h_foot = cv2.boundingRect(largest_contour_foot)

        # Assuming the largest contour is the reference object
        largest_contour_reference = max(contours_reference, key=cv2.contourArea)
        x_ref, y_ref, w_ref, h_ref = cv2.boundingRect(largest_contour_reference)

        # Calculate the pixel to cm ratio using the reference object
        pixel_to_cm_ratio = known_reference_size / w_ref

        # Calculate the foot size in cm
        foot_length_cm = h_foot * pixel_to_cm_ratio
        foot_width_cm = w_foot * pixel_to_cm_ratio

        # Optionally, draw the contours and bounding boxes on the images
        cv2.drawContours(foot_image, [largest_contour_foot], -1, (0, 255, 0), 2)
        cv2.rectangle(foot_image, (x_foot, y_foot), (x_foot + w_foot, y_foot + h_foot), (255, 0, 0), 2)

        cv2.drawContours(reference_image, [largest_contour_reference], -1, (0, 255, 0), 2)
        cv2.rectangle(reference_image, (x_ref, y_ref), (x_ref + w_ref, y_ref + h_ref), (255, 0, 0), 2)

        # Display the results
        cv2.imshow("Measured Foot", foot_image)
        cv2.imshow("Reference Object", reference_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        return foot_length_cm, foot_width_cm  # Return the measurements
    else:
        raise ValueError("No contours found for foot or reference object!")
