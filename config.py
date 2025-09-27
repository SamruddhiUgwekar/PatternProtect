# config.py
# Load settings from settings.json instead of environment variables

import json
import os

DEFAULTS = {
    "AWS_ACCESS_KEY_ID": "",
    "AWS_SECRET_ACCESS_KEY": "",
    "S3_BUCKET": "",
    "S3_REGION": "us-east-1",
    "SENDGRID_API_KEY": "",
    "LOCAL_STORAGE": "storage/uploaded_pdfs",
    "SIGNED_URL_EXPIRY": 86400
}

SETTINGS_FILE = "settings.json"

def load_config():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            try:
                data = json.load(f)
                cfg = DEFAULTS.copy()
                cfg.update(data)
                return cfg
            except Exception as e:
                print("Error loading settings.json:", e)
                return DEFAULTS
    else:
        return DEFAULTS

cfg = load_config()

AWS_ACCESS_KEY_ID = cfg["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = cfg["AWS_SECRET_ACCESS_KEY"]
S3_BUCKET = cfg["S3_BUCKET"]
S3_REGION = cfg["S3_REGION"]
SENDGRID_API_KEY = cfg["SENDGRID_API_KEY"]
LOCAL_STORAGE = cfg["LOCAL_STORAGE"]
SIGNED_URL_EXPIRY = int(cfg["SIGNED_URL_EXPIRY"])

os.makedirs(LOCAL_STORAGE, exist_ok=True)
