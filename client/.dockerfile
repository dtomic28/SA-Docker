FROM python:3.9-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app.py .

# Create templates directory and copy HTML template
RUN mkdir -p templates
COPY templates/index.html templates/

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application
CMD ["python", "app.py"]