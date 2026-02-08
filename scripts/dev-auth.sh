#!/usr/bin/env bash
set -e

CLUSTER_NAME=problemka
IMAGE=registry.example.com/problemka/auth:dev
DOCKERFILE=services/auth/Dockerfile
CONFIGMAP_NAME=problemka-env
ENV_FILE=env/.env.dev

echo "🧩 Creating/updating env ConfigMap..."
kubectl create configmap $CONFIGMAP_NAME \
  --from-env-file=$ENV_FILE \
  --dry-run=client -o yaml | kubectl apply -f -

echo "🚧 Building auth image..."
docker build \
  -f $DOCKERFILE \
  -t $IMAGE \
  .

echo "📦 Loading image into kind..."
kind load docker-image $IMAGE --name $CLUSTER_NAME

echo "📄 Applying auth manifests..."
kubectl apply -f k8s/auth.yaml

echo "♻️ Restarting auth deployment..."
kubectl rollout restart deploy/auth

echo "✅ Done"
echo "🌐 Swagger: http://api.domain.local/api/auth/docs"
