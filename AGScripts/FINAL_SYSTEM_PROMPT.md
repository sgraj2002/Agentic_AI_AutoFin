# AutoFin Loyalty Program: AI System Prompt Reference

This document serves as a comprehensive reference for any AI assistant working on the AutoFin Loyalty Program. It maps the final AWS-migrated architecture.

## 🏗️ System Architecture

- **Frontend**: Streamlit app (`src/app.py`) running on port 8510.
- **Backend**: FastAPI app (`src/api.py`) running on port 8001.
- **Orchestration**: LangGraph workflow (`src/graph.py`) coordinating agents.
- **Agents**:
  - `Screener`: Vision-based document extraction (Gemini Flash).
  - `Miner`: Database lookup for loyalty tiers.
  - `Calculator`: APR adjustment logic.
- **Database**: AWS RDS MySQL (`loyalty_db`).
- **Storage**: AWS S3 for document uploads.

## 🔐 Environment & Credentials

The application relies on the following environment variables (managed via Terraform in ECS):
- `GEMINI_API_KEY`: Google Generative AI key.
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`: RDS Connection details.
- `S3_BUCKET`: The target bucket for document processing.
- `USE_AWS`: Set to `true` for production deployment.

## 🚀 Infrastructure (Terraform)

Infrastructure is located in `AGImpl/terraform/`:
- `ecs.tf`: Task definitions, services, and environment config.
- `rds.tf`: MySQL instance and security groups.
- `s3.tf`: Bucket configuration.
- `networking.tf`: VPC, subnets, and routing.

## 🛠️ Key Commands

- **Local Build & Deploy**: `powershell -File AGScripts/deploy.ps1`
- **Infrastructure Update**: `terraform apply` in `AGImpl/terraform`
- **DB Check**: `GET http://<PUBLIC_IP>:8001/db-status`

## 🗒️ Evolution Notes
- The database auto-initializes and seeds "John Doe" (Platinum tier) on startup.
- Gemini responses are handled for both string and list formats in `agents.py`.
