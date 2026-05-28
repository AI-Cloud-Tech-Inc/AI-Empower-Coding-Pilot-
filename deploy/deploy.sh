#!/usr/bin/env bash
set -euo pipefail

# AI-Empower-Coding-Pilot — Deployment Script
# Usage: ./deploy/deploy.sh [docker|aws]

ENVIRONMENT="${1:-docker}"

echo "=== AI-Empower-Coding-Pilot Deployment ==="
echo "Environment: ${ENVIRONMENT}"

case "$ENVIRONMENT" in
  docker)
    echo "Building and deploying with Docker Compose..."
    docker compose -f docker-compose.prod.yml build
    docker compose -f docker-compose.prod.yml up -d
    echo "Waiting for services to be healthy..."
    sleep 10
    docker compose -f docker-compose.prod.yml ps
    echo ""
    echo "Backend:  http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo "Swagger:  http://localhost:8000/docs"
    ;;

  aws)
    echo "Deploying to AWS ECS..."
    REGION="${AWS_REGION:-us-east-1}"
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

    echo "Building and pushing Docker images to ECR..."
    aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"

    docker build -f docker/Dockerfile.backend -t ai-empower-backend .
    docker tag ai-empower-backend:latest "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/ai-empower-backend:latest"
    docker push "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/ai-empower-backend:latest"

    docker build -f docker/Dockerfile.frontend -t ai-empower-frontend .
    docker tag ai-empower-frontend:latest "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/ai-empower-frontend:latest"
    docker push "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/ai-empower-frontend:latest"

    echo "Updating ECS service..."
    aws ecs update-service --cluster ai-empower-cluster --service ai-empower-service --force-new-deployment --region "$REGION"

    echo "Deployment initiated. Monitor at: https://$REGION.console.aws.amazon.com/ecs"
    ;;

  *)
    echo "Unknown environment: $ENVIRONMENT"
    echo "Usage: $0 [docker|aws]"
    exit 1
    ;;
esac
