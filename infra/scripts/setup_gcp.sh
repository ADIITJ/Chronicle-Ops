#!/bin/bash
set -e

# Configuration
export GCLOUD_PATH=/Users/ashishdate/google-cloud-sdk/google-cloud-sdk/bin/gcloud
export PATH=$PATH:$(dirname $GCLOUD_PATH)

PROJECT_ID=${GCP_PROJECT_ID:-"chronicleops"}
REGION=${GCP_REGION:-"us-central1"}

echo "Setting up GCP project: $PROJECT_ID"

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  sql-component.googleapis.com \
  sqladmin.googleapis.com \
  storage-api.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com \
  --project=$PROJECT_ID

echo "GCP APIs enabled successfully"

# Create service account
gcloud iam service-accounts create chronicleops-sa \
  --display-name="ChronicleOps Service Account" \
  --project=$PROJECT_ID || true

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:chronicleops-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:chronicleops-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

echo "Service account created and configured"
echo "Setup complete!"
