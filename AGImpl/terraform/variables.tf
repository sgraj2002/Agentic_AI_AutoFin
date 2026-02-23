variable "aws_region" {
  description = "AWS region"
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name prefix for all resources"
  default     = "autofin-loyalty"
}

variable "db_password" {
  description = "RDS MySQL root password"
  type        = string
  sensitive   = true
}

variable "gemini_api_key" {
  description = "Gemini API key for AI processing"
  type        = string
  sensitive   = true
}

variable "account_id" {
  description = "AWS Account ID"
  default     = "173256371433"
}
