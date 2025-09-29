# config.py
# Load settings from settings.json instead of environment variables

import os

# Local fallback storage
LOCAL_STORAGE = "storage/uploaded_pdfs"
os.makedirs(LOCAL_STORAGE, exist_ok=True)

# AWS / S3 settings (loaded from env vars)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_REGION = os.getenv("S3_REGION", "us-east-1")

# Signed URL expiry in seconds (default 86400 = 24h)
SIGNED_URL_EXPIRY = int(os.getenv("SIGNED_URL_EXPIRY", "86400"))
