# 🛠️ AWS Console Setup Guide (Manual)

This guide provides step-by-step instructions to create all necessary AWS resources for the **AutoFin Loyalty Program** manually via the AWS Management Console.

---

## 1. Create an ECR Repository
1.  Search for **Elastic Container Registry** in the console.
2.  Click **Create repository**.
3.  **Repository name**: `autofin-loyalty`.
4.  Leave other settings as default and click **Create repository**.

## 2. Create an S3 Bucket
1.  Search for **S3** in the console.
2.  Click **Create bucket**.
3.  **Bucket name**: `autofin-loyalty-bucket-173256371433` (or your preferred unique name).
4.  **Region**: `us-east-1`.
5.  Keep defaults and click **Create bucket**.

## 3. Create an RDS MySQL Instance
1.  Search for **RDS** in the console.
2.  Click **Create database**.
3.  **Engine type**: `MySQL`.
4.  **Templates**: `Free tier`.
5.  **DB instance identifier**: `autofin-loyalty-db`.
6.  **Master username**: `admin`.
7.  **Master password**: (Set a strong password).
8.  **VPC**: Select your default VPC or project-specific VPC.
9.  **Public access**: `Yes` (for demo purposes) or `No` (recommended for production).
10. **Database name**: Click "Additional configuration" and set **Initial database name** to `loyalty_db`.
11. Click **Create database**.

## 4. Create an ECS Cluster
1.  Search for **Elastic Container Service**.
2.  Click **Clusters** -> **Create cluster**.
3.  **Cluster name**: `autofin-loyalty-cluster`.
4.  **Infrastructure**: Select `AWS Fargate (serverless)`.
5.  Click **Create**.

## 5. Create an ECS Task Definition
1.  In ECS, click **Task Definitions** -> **Create new task definition with JSON**.
2.  Use the `task_def.json` (archived) or the container configuration from `AGImpl/terraform/ecs.tf` as a reference.
3.  Ensure you add these **Environment Variables**:
    - `GEMINI_API_KEY`
    - `DB_HOST` (RDS Endpoint)
    - `DB_PORT` (3306)
    - `DB_USER` (`admin`)
    - `DB_PASSWORD`
    - `DB_NAME` (`loyalty_db`)
    - `S3_BUCKET`
    - `USE_AWS` (`true`)
4.  **Ports**: Map `8001` (FastAPI) and `8510` (Streamlit).
5.  **Task Role**: Ensure the execution role has `AmazonS3FullAccess` and `CloudWatchLogsFullAccess`.

## 6. Create an ECS Service
1.  Navigate to your cluster.
2.  In the **Services** tab, click **Create**.
3.  **Compute Options**: `Launch Type` -> `FARGATE`.
4.  **Family**: Select the Task Definition created in Step 5.
5.  **Service name**: `autofin-loyalty-service`.
6.  **Desired tasks**: `1`.
7.  **Networking**: Ensure a Public IP is assigned and the Security Group allows inbound traffic on ports `8001` and `8510`.
8.  Click **Create**.

---
*Note: Using Terraform is highly recommended for consistency and speed.*
