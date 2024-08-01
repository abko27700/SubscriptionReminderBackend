#!/bin/bash

# Define the source and destination paths
# SOURCE_PATH="/Users/abko/Desktop/secrets/.env"
SOURCE_PATH="/home/ec2-user/secrets/subs/.env"
DESTINATION_PATH=".env"
LOG_DIR="./logs"
LOG_FILE="$LOG_DIR/deployment.log"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to log messages
log_message() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Log the start of the script
log_message "Script started."

# Stop and remove the previous container if it exists
if [ "$(docker ps -q -f name=subscriptionreminder-container)" ]; then
    log_message "Stopping and removing existing container..."
    docker stop subscriptionreminder-container >> "$LOG_FILE" 2>&1
    docker rm subscriptionreminder-container >> "$LOG_FILE" 2>&1
fi

# Remove any unused Docker images
log_message "Removing unused Docker images..."
docker image prune -f >> "$LOG_FILE" 2>&1

# Check if the source file exists
if [ ! -f "$SOURCE_PATH" ]; then
    log_message "Source file $SOURCE_PATH does not exist."
    exit 1
fi

# Copy the .env file to the current directory
cp "$SOURCE_PATH" "$DESTINATION_PATH"

# Check if the copy was successful
if [ $? -eq 0 ]; then
    log_message ".env file copied successfully."
else
    log_message "Failed to copy .env file."
    exit 1
fi

# Build the Docker image
log_message "Building Docker image..."
docker build -t subscriptionreminder-backend . >> "$LOG_FILE" 2>&1

# Run the Docker container
log_message "Running Docker container..."
docker run -d -p 8000:8000 \
-v ~/.aws/credentials:/root/.aws/credentials \
-v ~/.aws/config:/root/.aws/config \
-v $(pwd):/app \
--name subscriptionreminder-container subscriptionreminder-backend >> "$LOG_FILE" 2>&1

# Log the end of the script
log_message "Script completed."
