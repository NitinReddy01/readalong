#!/bin/bash

# Exit immediately if any command fails
set -e

# AWS ECR Repository URL

# ECR_REPO_NAME="mdemo"
# AWS_REGION="ap-south-1"
# AWS_ACCOUNT_ID="381492052143"
# TAG="latest"

# # Authenticate with AWS ECR
# echo "Authenticating with AWS ECR..."
# aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# # Build and push Docker image directly to ECR
# echo "Building and pushing Docker image..."
# docker buildx build \
#   --platform linux/amd64 \
#   --provenance=false \
#   --push \
#   -t $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:$TAG \
#   .

# echo "Deployment completed successfully"

# Docker Hub image tag (username/repo:tag)
IMAGE_TAG="agastya29/voiceapi:latest"
echo "Building and pushing Docker image to Docker Hub..."
docker buildx build \
  --platform linux/amd64 \
  --provenance=false \
  --push \
  -t $IMAGE_TAG \
  .

echo "Deployment to Docker Hub completed successfully"