from flask import Flask, render_template
import requests
import time
import threading
import os
import json

app = Flask(__name__)

# Global variable to store the latest image
latest_image = None
image_lock = threading.Lock()

# Server address (will be set via environment variable)
SERVER_URL = os.environ.get("SERVER_URL", "http://server:5000")


def fetch_images():
    """
    Fetch images from the server periodically
    """
    global latest_image

    while True:
        try:
            # Get the image from the server
            response = requests.get(f"{SERVER_URL}/image")

            if response.status_code == 200:
                # Store the base64 encoded image
                with image_lock:
                    latest_image = response.json().get("image")
            else:
                print(f"Failed to fetch image: {response.status_code}")

            # Sleep for a bit before fetching again (shorter than server's interval)
            time.sleep(5)
        except Exception as e:
            print(f"Error in fetch_images: {e}")
            time.sleep(5)


@app.route("/")
def index():
    """
    Render the main page with the latest image
    """
    global latest_image

    with image_lock:
        current_image = latest_image

    return render_template("index.html", image=current_image)


if __name__ == "__main__":
    # Start the image fetching thread
    fetch_thread = threading.Thread(target=fetch_images)
    fetch_thread.daemon = True
    fetch_thread.start()

    # Start the Flask server
    app.run(host="0.0.0.0", port=8080)
