#!/usr/bin/env bash
set -e

CLUSTER_NAME=problemka
IMAGE=registry.example.com/problemka/auth:dev
DOCKERFILE=services/auth/Dockerfile
SECRET_NAME=auth-secrets
ENV_FILE=env/.env.dev

echo "🔐 Creating/updating secrets..."

kubectl delete secret $SECRET_NAME --ignore-not-found

kubectl create secret generic $SECRET_NAME \
  --from-env-file=$ENV_FILE

echo "🚧 Building auth image..."
docker build \
  -f $DOCKERFILE \
  -t $IMAGE \
  .

echo "📦 Loading image into kind..."
kind load docker-image $IMAGE --name $CLUSTER_NAME

echo "♻️ Restarting auth deployment..."
kubectl rollout restart deploy/auth

echo "✅ Done"
echo "🌐 Swagger: http://api.domain.local/api/auth/docs"
