#!/usr/bin/env bash
set -euo pipefail

ENV_FILE=${ENV_FILE:-env/.env.dev}
CONFIGMAP_NAME=${CONFIGMAP_NAME:-problemka-env}
APPLY_INGRESS=${APPLY_INGRESS:-1}

echo "🧩 Creating/updating env ConfigMap..."
kubectl create configmap "$CONFIGMAP_NAME" \
  --from-env-file="$ENV_FILE" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "📄 Applying backend manifests..."
kubectl apply -f k8s/auth.yaml
kubectl apply -f k8s/reports.yaml

if [ "$APPLY_INGRESS" = "1" ]; then
  echo "🌐 Applying ingress..."
  kubectl apply -f k8s/ingress.yaml
fi

echo "✅ Done"
