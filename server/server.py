from flask import Flask, jsonify
import numpy as np
import cv2
import time
import threading
import base64

app = Flask(__name__)

# Global variable to store the latest image
latest_image = None
image_lock = threading.Lock()


def generate_dummy_image():
    """
    Generate a dummy image with timestamp when camera is not available
    """
    # Create a base image
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    img[:] = (50, 30, 20)  # BGR format

    # Add a simple pattern
    cv2.rectangle(img, (100, 100), (540, 380), (0, 0, 255), -1)  # Red rectangle
    cv2.circle(img, (320, 240), 80, (0, 255, 0), -1)  # Green circle

    # Add text indicating this is a dummy image
    cv2.putText(
        img,
        "Camera Not Available",
        (180, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2,
    )

    # Add current timestamp
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(
        img, timestamp, (180, 420), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2
    )

    return img


def capture_images():
    """
    Capture images from camera or generate dummy images every 10 seconds
    """
    global latest_image

    # Try to initialize camera
    camera = None
    try:
        camera = cv2.VideoCapture(0)
        if camera.isOpened():
            camera = None
            print("Camera initialized successfully")
        else:
            print("Camera could not be opened, using dummy images")
            camera = None
    except Exception as e:
        print(f"Error initializing camera: {e}")
        camera = None

    # Generate initial image
    if camera is not None and camera.isOpened():
        ret, frame = camera.read()
        if ret:
            # Add timestamp to the image
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(
                frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
            )
            with image_lock:
                latest_image = frame
        else:
            with image_lock:
                latest_image = generate_dummy_image()
    else:
        with image_lock:
            latest_image = generate_dummy_image()

    while True:
        try:
            if camera is not None and camera.isOpened():
                # Try to get frame from camera
                ret, frame = camera.read()
                if ret:
                    # Add timestamp to the image
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    cv2.putText(
                        frame,
                        timestamp,
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2,
                    )
                    with image_lock:
                        latest_image = frame
                else:
                    # Fall back to dummy image if frame capture fails
                    with image_lock:
                        latest_image = generate_dummy_image()
            else:
                # Use dummy image if no camera
                with image_lock:
                    latest_image = generate_dummy_image()

            # Sleep for 10 seconds
            time.sleep(10)
        except Exception as e:
            print(f"Error in capture_images: {e}")
            # If any error occurs, use dummy image
            with image_lock:
                latest_image = generate_dummy_image()
            time.sleep(10)


@app.route("/image", methods=["GET"])
def get_image():
    """
    Return the latest captured image as a JPEG
    """
    global latest_image

    with image_lock:
        if latest_image is None:
            return jsonify({"error": "No image available"}), 404

        # Convert the image to JPEG
        _, buffer = cv2.imencode(".jpg", latest_image)
        jpg_as_text = base64.b64encode(buffer).decode("utf-8")

    return jsonify({"image": jpg_as_text})


if __name__ == "__main__":
    # Start the image capture thread
    capture_thread = threading.Thread(target=capture_images)
    capture_thread.daemon = True
    capture_thread.start()

    # Start the Flask server
    app.run(host="0.0.0.0", port=5000)
