#!/bin/bash

# Define the source and destination paths
# 


SOURCE_PATH="/Users/abko/Desktop/secrets/.env"
DESTINATION_PATH=".env"

# Stop and remove the previous container if it exists
if [ "$(docker ps -q -f name=subscriptionreminder-container)" ]; then
    echo "Stopping and removing existing container..."
    docker stop subscriptionreminder-container
    docker rm subscriptionreminder-container
fi

# Check if the source file exists
if [ ! -f "$SOURCE_PATH" ]; then
    echo "Source file $SOURCE_PATH does not exist."
    exit 1
fi

# Build the Docker image
docker build -t subscriptionreminder-backend .

# Copy the .env file to the current directory
cp "$SOURCE_PATH" "$DESTINATION_PATH"

# Check if the copy was successful
if [ $? -eq 0 ]; then
    echo ".env file copied successfully."
else
    echo "Failed to copy .env file."
    exit 1
fi

# Run the Docker container
docker run -d -p 8000:8000 \
-v ~/.aws/credentials:/root/.aws/credentials \
-v ~/.aws/config:/root/.aws/config \
-v $(pwd):/app \
--name subscriptionreminder-container subscriptionreminder-backend
