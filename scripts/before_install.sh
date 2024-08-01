#!/bin/bash

# Define the paths
PROJECT_DIR="/home/ec2-user/projectDaria/SubscriptionReminderBackend"
BACKUP_DIR="/home/ec2-user/projectDaria/backup"

# Create a backup of the current project if it exists
if [ -d "$PROJECT_DIR" ]; then
    echo "Backing up the current project directory..."
    mkdir -p "$BACKUP_DIR"
    tar -czf "$BACKUP_DIR/SubscriptionReminderBackend_$(date +%F_%T).tar.gz" -C "$PROJECT_DIR" .
    if [ $? -eq 0 ]; then
        echo "Backup created successfully."
    else
        echo "Failed to create backup."
        exit 1
    fi
else
    echo "No existing project directory found to back up."
fi

# Stop the running Docker container if it exists
if [ "$(docker ps -q -f name=subscriptionreminder-container)" ]; then
    echo "Stopping existing Docker container..."
    docker stop subscriptionreminder-container
    docker rm subscriptionreminder-container
fi

# Clean up old Docker images if needed
echo "Removing old Docker images..."
docker image prune -f

# Other tasks can be added here if needed

echo "Before-install script completed."
