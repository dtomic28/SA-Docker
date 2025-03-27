FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY server.py .

# Create a dummy image for when camera is not available
RUN mkdir -p static
RUN echo -e "P6\n640 480\n255\n$(dd if=/dev/zero bs=1 count=$((640*480*3)) | tr '\0' '\377')" > static/dummy.jpg

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]