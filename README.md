# 🚗 Serverless Car Repair Management System

A cloud-native application designed to streamline car repair requests. This system leverages a fully serverless architecture on AWS, allowing customers to submit repair tickets that are automatically stored in a database and trigger immediate notifications to the workshop staff.

## 🏗 Architecture

The solution uses an Event-Driven Architecture:

1.  **Frontend:** Static HTML/JS website hosted on **Amazon S3**.
2.  **API:** **Amazon API Gateway** (HTTP API) serves as the entry point.
3.  **Compute:** **AWS Lambda** (Python) processes the requests.
4.  **Database:** **Amazon DynamoDB** stores repair details (ID, Car Model, Description, Status).
5.  **Notifications:** **Amazon SNS** sends alerts (e.g., email) when a new ticket is created.

## 🛠 Tech Stack

* **Infrastructure as Code:** AWS CloudFormation (YAML)
* **Backend Runtime:** Python 3.9
* **Frontend:** HTML5, CSS3, Vanilla JavaScript (Fetch API)
* **AWS Services:** Lambda, API Gateway, DynamoDB, SNS, S3, IAM

## 📂 Project Structure

```text
SERVERLESS-CAR-REPAIR-MANAGEMENT-SYSTEM/
│
├── frontend/
│   └── index.html          # User Interface & API integration logic
│
├── infrastructure/
│   └── template.yaml       # CloudFormation template defining AWS resources
│
├── src/
│   └── lambda_function.py  # Backend logic (DB interactions & SNS publishing)
│
└── README.md            

## 📋 Prerequisites

Before deploying, ensure you have the following installed:
* **AWS CLI** (Configured with `aws configure`)
* **Python 3.9+**
* **Zip** utility (for packaging Lambda)

## 🚀 Deployment Guide

### 1. Package the Lambda Function
AWS CloudFormation requires the Lambda code to be zipped and uploaded to S3 (or defined inline if short, but zipping is best practice).

```bash
# Zip the source code
cd src
zip -r ../lambda_function.zip .
cd ..

# Upload to your S3 artifact bucket (replace with your bucket name)
aws s3 cp lambda_function.zip s3://YOUR-ARTIFACT-BUCKET-NAME/