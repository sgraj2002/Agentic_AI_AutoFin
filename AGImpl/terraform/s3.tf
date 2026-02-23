resource "aws_s3_bucket" "paystubs" {
  bucket        = "${var.project_name}-bucket-${var.account_id}"
  force_destroy = true

  tags = {
    Name = "${var.project_name}-bucket"
  }
}

resource "aws_s3_bucket_public_access_block" "paystubs" {
  bucket = aws_s3_bucket.paystubs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
