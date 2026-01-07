#!/usr/bin/env bash
set -e

CLUSTER_NAME=problemka
IMAGE=registry.example.com/problemka/reports:dev
DOCKERFILE=services/reports/Dockerfile
SECRET_NAME=reports-secrets
ENV_FILE=env/.env.dev

echo "🔐 Creating/updating reports secrets..."

kubectl delete secret $SECRET_NAME --ignore-not-found

kubectl create secret generic $SECRET_NAME \
  --from-env-file=$ENV_FILE

echo "🚧 Building reports image..."
docker build \
  -f $DOCKERFILE \
  -t $IMAGE \
  .

echo "📦 Loading image into kind..."
kind load docker-image $IMAGE --name $CLUSTER_NAME

echo "♻️ Restarting reports deployment..."
kubectl rollout restart deploy/reports

echo "✅ Done"
echo "🌐 Reports docs: http://api.domain.local/api/reports/docs"
