from flask import Flask, Response, jsonify
import cv2
import time
import threading
import os
import base64

app = Flask(__name__)

# Global variable to store the latest image
latest_image = None
image_lock = threading.Lock()


def capture_images():
    """
    Capture images every 10 seconds from the camera
    """
    global latest_image

    # Initialize camera
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Error: Could not open camera.")
        # If no camera available, use a solid color image for testing
        dummy_image = cv2.imread("dummy.jpg") if os.path.exists("dummy.jpg") else None
        if dummy_image is None:
            # Create a black image if no dummy image available
            dummy_image = cv2.rectangle(
                cv2.cvtColor(
                    cv2.imread("dummy.jpg")
                    if os.path.exists("dummy.jpg")
                    else cv2.cvtColor(
                        255 * cv2.imread(os.path.join("static", "dummy.jpg"))
                        if os.path.exists(os.path.join("static", "dummy.jpg"))
                        else cv2.Mat(480, 640, cv2.CV_8UC3, (0, 0, 0)),
                        cv2.COLOR_BGR2RGB,
                    ),
                    cv2.COLOR_RGB2BGR,
                ),
                (100, 100),
                (540, 380),
                (0, 0, 255),
                -1,
            )

        # Add timestamp to the dummy image
        with image_lock:
            latest_image = dummy_image

    while True:
        try:
            if camera.isOpened():
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

                    # Update the latest image
                    with image_lock:
                        latest_image = frame
                else:
                    print("Failed to capture image")
            else:
                # If camera is not available, update timestamp on dummy image
                with image_lock:
                    if latest_image is not None:
                        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                        latest_image = latest_image.copy()
                        cv2.putText(
                            latest_image,
                            timestamp,
                            (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 255, 0),
                            2,
                        )

            # Sleep for 10 seconds
            time.sleep(10)
        except Exception as e:
            print(f"Error in capture_images: {e}")
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
