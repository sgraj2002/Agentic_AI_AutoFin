# Complete AWS Deployment Script for AutoFin Loyalty Program
# Builds Docker image, pushes to ECR, and deploys to ECS

# Configuration
$REGION = "us-east-1"
$ACCOUNT_ID = "173256371433"
$REPO_NAME = "autofin-loyalty"
$IMAGE_TAG = "latest"
$CLUSTER_NAME = "autofin-loyalty-cluster"
$SERVICE_NAME = "autofin-loyalty-service"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AutoFin AWS Deployment Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Login to ECR
Write-Host "[1/6] Logging in to ECR..." -ForegroundColor Yellow
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ECR login failed!" -ForegroundColor Red
    exit 1
}
Write-Host "ECR login successful" -ForegroundColor Green
Write-Host ""

# Step 2: Build the Docker image
Write-Host "[2/6] Building Docker image..." -ForegroundColor Yellow
docker build -t $REPO_NAME -f ../AGImpl/Dockerfile ../AGImpl

if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "Docker image built successfully" -ForegroundColor Green
Write-Host ""

# Step 3: Tag the image
Write-Host "[3/6] Tagging Docker image..." -ForegroundColor Yellow
docker tag "${REPO_NAME}:latest" "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/${REPO_NAME}:${IMAGE_TAG}"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker tag failed!" -ForegroundColor Red
    exit 1
}
Write-Host "Image tagged successfully" -ForegroundColor Green
Write-Host ""

# Step 4: Push to ECR
Write-Host "[4/6] Pushing image to ECR..." -ForegroundColor Yellow
docker push "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/${REPO_NAME}:${IMAGE_TAG}"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker push failed!" -ForegroundColor Red
    exit 1
}
Write-Host "Image pushed to ECR successfully" -ForegroundColor Green
Write-Host ""

# Step 5: Force new ECS deployment
Write-Host "[5/6] Deploying to ECS..." -ForegroundColor Yellow
aws ecs update-service `
    --cluster $CLUSTER_NAME `
    --service $SERVICE_NAME `
    --force-new-deployment `
    --region $REGION `
    --no-cli-pager

if ($LASTEXITCODE -ne 0) {
    Write-Host "ECS deployment failed!" -ForegroundColor Red
    exit 1
}
Write-Host "ECS deployment initiated" -ForegroundColor Green
Write-Host ""

# Step 6: Wait for deployment to stabilize
Write-Host "[6/6] Waiting for deployment to complete..." -ForegroundColor Yellow
Write-Host "This may take 5-10 minutes. Please wait..." -ForegroundColor Gray

aws ecs wait services-stable `
    --cluster $CLUSTER_NAME `
    --services $SERVICE_NAME `
    --region $REGION

if ($LASTEXITCODE -ne 0) {
    Write-Host "Deployment did not stabilize!" -ForegroundColor Red
    Write-Host "Check ECS console for details: https://console.aws.amazon.com/ecs" -ForegroundColor Yellow
    exit 1
}

Write-Host "Deployment completed successfully!" -ForegroundColor Green
Write-Host ""

# Get public IP of the deployed task
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Deployment Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$TASK_ARN = aws ecs list-tasks `
    --cluster $CLUSTER_NAME `
    --service-name $SERVICE_NAME `
    --region $REGION `
    --query 'taskArns[0]' `
    --output text

if ($TASK_ARN -and $TASK_ARN -ne "None") {
    $ENI_ID = aws ecs describe-tasks `
        --cluster $CLUSTER_NAME `
        --tasks $TASK_ARN `
        --region $REGION `
        --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' `
        --output text

    $PUBLIC_IP = aws ec2 describe-network-interfaces `
        --network-interface-ids $ENI_ID `
        --region $REGION `
        --query 'NetworkInterfaces[0].Association.PublicIp' `
        --output text

    Write-Host ""
    Write-Host "Streamlit UI:   http://${PUBLIC_IP}:8510" -ForegroundColor Green
    Write-Host "FastAPI Backend: http://${PUBLIC_IP}:8001" -ForegroundColor Green
    Write-Host "ECS Console:    https://console.aws.amazon.com/ecs/v2/clusters/$CLUSTER_NAME/services/$SERVICE_NAME" -ForegroundColor Cyan
    Write-Host "CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home?region=$REGION#logsV2:log-groups/log-group//ecs/$REPO_NAME" -ForegroundColor Cyan
} else {
    Write-Host "Could not retrieve task information" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Deployment Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
