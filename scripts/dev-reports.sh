#!/usr/bin/env bash
set -e

CLUSTER_NAME=problemka
IMAGE=registry.example.com/problemka/reports:dev
DOCKERFILE=services/reports/Dockerfile
CONFIGMAP_NAME=problemka-env
ENV_FILE=env/.env.dev

echo "🧩 Creating/updating env ConfigMap..."
kubectl create configmap $CONFIGMAP_NAME \
  --from-env-file=$ENV_FILE \
  --dry-run=client -o yaml | kubectl apply -f -

echo "🚧 Building reports image..."
docker build \
  -f $DOCKERFILE \
  -t $IMAGE \
  .

echo "📦 Loading image into kind..."
kind load docker-image $IMAGE --name $CLUSTER_NAME

echo "📄 Applying reports manifests..."
kubectl apply -f k8s/reports.yaml

echo "♻️ Restarting reports deployment..."
kubectl rollout restart deploy/reports

echo "✅ Done"
echo "🌐 Reports docs: http://api.domain.local/api/reports/docs"
