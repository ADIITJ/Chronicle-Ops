#!/bin/bash
set -e

export GCLOUD=/Users/ashishdate/google-cloud-sdk/google-cloud-sdk/bin/gcloud
export PATH=$PATH:$(dirname $GCLOUD)

PROJECT_ID=${GCP_PROJECT_ID:-"chronicleops-prod"}
REGION="us-central1"

echo "=== ChronicleOps GCP Deployment ==="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"

echo "Step 1: Creating Cloud SQL instance..."
$GCLOUD sql instances create chronicleops-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=$REGION \
  --root-password=chronicleops-root-$(openssl rand -hex 16) \
  --storage-type=SSD \
  --storage-size=10GB \
  --backup-start-time=03:00 \
  --enable-bin-log \
  --project=$PROJECT_ID || echo "Instance may already exist"

echo "Step 2: Creating database..."
$GCLOUD sql databases create chronicleops \
  --instance=chronicleops-db \
  --project=$PROJECT_ID || echo "Database may already exist"

echo "Step 3: Creating database user..."
DB_PASSWORD=$(openssl rand -hex 32)
$GCLOUD sql users create chronicleops \
  --instance=chronicleops-db \
  --password=$DB_PASSWORD \
  --project=$PROJECT_ID || echo "User may already exist"

echo "Step 4: Getting Cloud SQL connection name..."
CONNECTION_NAME=$($GCLOUD sql instances describe chronicleops-db \
  --project=$PROJECT_ID \
  --format='value(connectionName)')

DATABASE_URL="postgresql://chronicleops:$DB_PASSWORD@/$CONNECTION_NAME/chronicleops?host=/cloudsql/$CONNECTION_NAME"

echo "Step 5: Creating secrets..."
echo -n "$DATABASE_URL" | $GCLOUD secrets create database-url \
  --data-file=- \
  --replication-policy=automatic \
  --project=$PROJECT_ID || echo "Secret may already exist"

echo -n "redis-host" | $GCLOUD secrets create redis-host \
  --data-file=- \
  --replication-policy=automatic \
  --project=$PROJECT_ID || echo "Secret may already exist"

echo -n "https://chronicleops-backend-REPLACE.run.app" | $GCLOUD secrets create api-url \
  --data-file=- \
  --replication-policy=automatic \
  --project=$PROJECT_ID || echo "Secret may already exist"

echo "Step 6: Creating Cloud Storage bucket..."
$GCLOUD storage buckets create gs://$PROJECT_ID-artifacts \
  --location=$REGION \
  --uniform-bucket-level-access \
  --project=$PROJECT_ID || echo "Bucket may already exist"

echo "Step 7: Enabling Cloud Build..."
$GCLOUD services enable cloudbuild.googleapis.com --project=$PROJECT_ID

echo "Step 8: Granting Cloud Build permissions..."
PROJECT_NUMBER=$($GCLOUD projects describe $PROJECT_ID --format='value(projectNumber)')

$GCLOUD projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com \
  --role=roles/run.admin

$GCLOUD projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com \
  --role=roles/iam.serviceAccountUser

$GCLOUD projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor

echo "Step 9: Submitting Cloud Build..."
$GCLOUD builds submit --config=cloudbuild.yaml --project=$PROJECT_ID .

echo "=== Deployment Complete ==="
echo "Backend URL: https://chronicleops-backend-REPLACE.run.app"
echo "Frontend URL: https://chronicleops-frontend-REPLACE.run.app"
