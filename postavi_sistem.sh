#!/bin/bash

# Exit on error
set -e

echo "Setting up Docker network..."
# Create a Docker network if it doesn't exist
NETWORK_NAME="camera_network"
if ! docker network inspect $NETWORK_NAME &>/dev/null; then
    docker network create $NETWORK_NAME
    echo "Created network: $NETWORK_NAME"
else
    echo "Network $NETWORK_NAME already exists"
fi

echo "Building server container..."
# Build the server Docker image
docker build -t camera-server -f server/.Dockerfile server

echo "Building client container..."
# Build the client Docker image
docker build -t camera-client -f client/.Dockerfile client

echo "Starting server container..."
# Run the server container
if [ -e /dev/video0 ]; then
    echo "Camera device found, starting server with camera access..."
    # Run the server container with camera access
    docker run -d --name camera-server \
        --restart unless-stopped \
        --network $NETWORK_NAME \
        --device /dev/video0:/dev/video0 \
        camera-server
else
    echo "No camera device found, starting server without camera access..."
    # Run the server container without camera access
    docker run -d --name camera-server \
        --restart unless-stopped \
        --network $NETWORK_NAME \
        camera-server
fi
echo "Starting client container..."
# Run the client container
docker run -d --name camera-client \
    --restart unless-stopped \
    --network $NETWORK_NAME \
    -e SERVER_URL=http://camera-server:5000 \
    -p 8080:8080 \
    camera-client

# Get the client container's IP address
CLIENT_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' camera-client)
echo "Client IP address: $CLIENT_IP"
echo "Access the client at http://$CLIENT_IP:8080 or http://localhost:8080"