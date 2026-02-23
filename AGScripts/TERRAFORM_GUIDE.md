# 🏗️ Terraform Execution Guide

This document explains how to use Terraform to provision and manage the infrastructure for the **AutoFin Loyalty Program**.

---

## 📂 File Structure
All Terraform files are located in `AGImpl/terraform/`:
- `main.tf`: Provider setup (AWS region: `us-east-1`).
- `ecs.tf`: ECS Cluster, Service, and Task Definition.
- `rds.tf`: RDS MySQL database and security groups.
- `s3.tf`: S3 bucket for document storage.
- `ecr.tf`: Container registry repository.
- `networking.tf`: VPC, Subnets, Gateways, and Security Groups.
- `iam.tf`: Roles and Policies for ECS tasks.
- `terraform.tfvars`: **Local only** (contains your sensitive secrets).

---

## 🚀 Execution Steps

### 1. Initialization
Downloads the required AWS providers.
```powershell
cd AGImpl/terraform
terraform init
```

### 2. Configuration
Create a `terraform.tfvars` file (use `terraform.tfvars.example` as a template).
- `gemini_api_key`: Your Google AI Key.
- `db_password`: The password for the RDS MySQL administrator.

### 3. Planning
Verify what changes Terraform will make without applying them.
```powershell
terraform plan
```

### 4. Deployment
Provision the infrastructure to AWS.
```powershell
terraform apply
```
*Note: You will be prompted to type `yes` to confirm.*

---

## 🔧 Management Commands

- **Update Environment**: If you change an environment variable in `ecs.tf`, run `terraform apply` again. It will update the Task Definition automatically.
- **View Outputs**: View your Public IP and RDS Endpoint anytime.
  ```powershell
  terraform output
  ```
- **Teardown**: Remove all AWS resources to avoid costs.
  ```powershell
  terraform destroy
  ```

---

## 💡 Important Notes
- **State Management**: Terraform keeps track of your infrastructure in `terraform.tfstate`. **Do not delete this file**, as it's needed to update or destroy the resources later.
- **Sensitive Data**: Never commit `terraform.tfvars` or `*.tfstate` to public repositories. They are already in our `.gitignore`.
