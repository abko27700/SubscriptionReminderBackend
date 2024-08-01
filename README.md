# Subscription Reminder App

## Overview
The Subscription Reminder App is a full-stack application designed to help users manage and track their subscription services. This project showcases a backend API built with Flask, containerized with Docker, and deployed on an EC2 instance. The frontend is developed using Next.js and is hosted as static pages on AWS S3, utilizing CloudFront for distribution.

## Features
- **Subscription Management**: Users can add, manage, and disable subscriptions.
- **Reminders**: Set reminders for upcoming subscription bills. Notifications are sent via AWS SNS.
- **Database**: Utilizes DynamoDB for efficient data storage and retrieval.

## Deployment
- **Backend**: Dockerized Flask application running on an EC2 instance.
- **Frontend**: Static pages hosted on AWS S3, with CloudFront as the CDN.
- **CI/CD**: Code updates are pushed to EC2 via GitHub Actions and AWS CodeDeploy.

## Architecture
- **Frontend**: Next.js application
- **Backend**: Flask API
- **Database**: DynamoDB
- **Notifications**: Lambda functions using SMTP(AWS SES)
- **Deployment**: Docker, EC2, GitHub Actions, AWS CodeDeploy

For any further information, feel free to contact me at b.kothari@ufl.edu
