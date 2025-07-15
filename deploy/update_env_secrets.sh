#!/bin/bash
set -a
source prod.env
set +a

# 拼接 env vars 字串
ENV_VARS="\
MONGO_URL=${MONGO_URL},\
GCP_STORAGE_BUCKET=${GCP_STORAGE_BUCKET},\
FRONTEND_URL=${FRONTEND_URL},\
GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS},\
CLERK_SECRET_KEY=${CLERK_SECRET_KEY},\
CLERK_JWT_PUB_KEY=${CLERK_JWT_PUB_KEY}"

echo "ENV_VARS: $ENV_VARS"

# 執行 gcloud 部署指令
gcloud run services update backend-app \
  --update-env-vars "$ENV_VARS" \
  --set-secrets /secrets/gcp/sa-key.json=auto-labeling-sa:latest \
  --set-secrets /secrets/clerk/public.pem=auto-labeling-jwt-public:latest