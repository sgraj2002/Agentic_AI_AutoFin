# AWS Infrastructure Migration Plan

## Current AWS Environment (Confirmed)

| Resource | Status | Details |
|----------|--------|---------|
| **Account** | ✅ Active | `173256371433` |
| **Region** | ✅ Configured | `us-east-1` |
| **ECS Cluster** | ✅ Exists | `resume-matcher-cluster` (from previous project) |
| **ECR Repo** | ✅ Exists | `resume-matcher` (from previous project) |
| **RDS MySQL** | ❌ Not found | No instances in `us-east-1` |
| **S3 Buckets** | ❌ Not found | No buckets exist |

> [!IMPORTANT]
> The existing ECS cluster and ECR repo belong to your previous `resume-matcher` project. We will **create new, dedicated resources** for the AutoFin Loyalty Program to keep them separate and clean.

---

## Proposed Changes

### 1. Containerization

#### [NEW] [Dockerfile](file:///c:/Users/Agentic_AI_AutoFin/AGImpl/Dockerfile)
- Python 3.11 slim base image
- Installs dependencies from `requirements.txt`
- Runs FastAPI + Streamlit via `supervisord` (single container, two processes)
- Exposes ports `8001` (FastAPI) and `8510` (Streamlit)

---

### 2. AWS ECR (Container Registry)

#### [NEW] ECR Repository: `autofin-loyalty`
- Create a dedicated ECR repo for this project
- Push script will build, tag, and push the Docker image

#### [NEW] [deploy.ps1](file:///c:/Users/Agentic_AI_AutoFin/AGScripts/deploy.ps1)
- Modeled after your existing `deploy-to-aws.ps1` pattern
- Steps: ECR Login → Build → Tag → Push → ECS Deploy → Wait for Stability

---

### 3. AWS RDS MySQL (New)

#### [NEW] RDS MySQL Instance: `autofin-loyalty-db`
- **Engine**: MySQL 8.0
- **Instance Class**: `db.t3.micro` (Free Tier eligible)
- **Database**: `loyalty_db`
- **Port**: `3306`
- Seed data from existing `init.sql`:
  - `users` table with `John Doe / Platinum / 1234`
  - `applications` table

---

### 4. AWS S3 (New)

#### [NEW] S3 Bucket: `autofin-loyalty-bucket-173256371433`
- Stores uploaded paystub documents
- Replaces LocalStack S3

---

### 5. AWS ECS Fargate (New Service)

#### [NEW] ECS Cluster: `autofin-loyalty-cluster`
- Dedicated cluster (separate from `resume-matcher-cluster`)

#### [NEW] ECS Task Definition
- **CPU**: 512 | **Memory**: 1024
- Container image from ECR `autofin-loyalty:latest`
- Environment variables: `GEMINI_API_KEY`, `DB_HOST`, `DB_PASSWORD`, `S3_BUCKET`
- Port mappings: `8001` (FastAPI), `8510` (Streamlit)

#### [NEW] ECS Service: `autofin-loyalty-service`
- Fargate launch type
- Public IP assigned (for demo access)
- Security group allowing inbound on ports `8001` and `8510`

---

### 6. Terraform Files

#### [NEW] [terraform/](file:///c:/Users/Agentic_AI_AutoFin/AGImpl/terraform)

| File | Purpose |
|------|---------|
| `main.tf` | AWS provider, region `us-east-1` |
| `ecr.tf` | ECR repository `autofin-loyalty` |
| `s3.tf` | S3 bucket for paystub storage |
| `rds.tf` | RDS MySQL `db.t3.micro` instance |
| `ecs.tf` | ECS cluster, task definition, service |
| `iam.tf` | Task execution role with S3/RDS/ECR access |
| `networking.tf` | VPC, subnets, security groups |
| `outputs.tf` | Public IP, RDS endpoint, S3 bucket name |
| `variables.tf` | Configurable inputs (DB password, Gemini key) |

---

### 7. Code Changes for AWS

#### [MODIFY] [agents.py](file:///c:/Users/Agentic_AI_AutoFin/AGImpl/src/agents.py)
- S3 client: Remove hardcoded LocalStack endpoint; use real AWS S3
- MySQL: Read `DB_HOST`, `DB_PASSWORD` from environment variables instead of `localhost:3307`

#### [MODIFY] [api.py](file:///c:/Users/Agentic_AI_AutoFin/AGImpl/src/api.py)
- S3 upload: Remove LocalStack endpoint; use real AWS S3

---

## Verification Plan

### Automated
- `terraform plan` → verify no errors
- `docker build` → verify image builds
- `deploy.ps1` → push and deploy

### Manual
1. Access Streamlit via ECS public IP
2. Upload a paystub → verify S3 storage
3. Process with AI → verify Gemini extraction
4. Check RDS → verify loyalty tier lookup
5. Full end-to-end "Lock APR" flow
