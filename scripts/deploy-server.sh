#!/usr/bin/env bash
set -euo pipefail

ENV_FILE=${ENV_FILE:-env/.env.dev}
CONFIGMAP_NAME=${CONFIGMAP_NAME:-problemka-env}
APPLY_INGRESS=${APPLY_INGRESS:-1}

AUTH_IMAGE=${AUTH_IMAGE:-registry.example.com/problemka/auth:dev}
REPORTS_IMAGE=${REPORTS_IMAGE:-registry.example.com/problemka/reports:dev}

AUTH_DOCKERFILE=${AUTH_DOCKERFILE:-services/auth/Dockerfile}
REPORTS_DOCKERFILE=${REPORTS_DOCKERFILE:-services/reports/Dockerfile}

if ! command -v k3s >/dev/null 2>&1; then
  echo "📦 Installing k3s..."
  # Disable Traefik so host nginx can keep 80/443.
  curl -sfL https://get.k3s.io | sh -s - --disable traefik
fi

KUBECTL="sudo k3s kubectl"

echo "🌐 Ensuring ingress-nginx is installed..."
$KUBECTL apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.14.2/deploy/static/provider/baremetal/deploy.yaml

echo "🔧 Ensuring ingress-nginx NodePort is fixed to 30080/30443..."
$KUBECTL -n ingress-nginx patch svc ingress-nginx-controller --type='merge' -p '{
  "spec": {
    "type": "NodePort",
    "ports": [
      {"name":"http","port":80,"protocol":"TCP","targetPort":"http","nodePort":30080},
      {"name":"https","port":443,"protocol":"TCP","targetPort":"https","nodePort":30443}
    ]
  }
}'

echo "🧩 Creating/updating env ConfigMap..."
$KUBECTL create configmap "$CONFIGMAP_NAME" \
  --from-env-file="$ENV_FILE" \
  --dry-run=client -o yaml | $KUBECTL apply -f -

echo "🚧 Building auth image..."
docker build -f "$AUTH_DOCKERFILE" -t "$AUTH_IMAGE" .
echo "📦 Importing auth image into k3s..."
docker save "$AUTH_IMAGE" | sudo k3s ctr images import -

echo "🚧 Building reports image..."
docker build -f "$REPORTS_DOCKERFILE" -t "$REPORTS_IMAGE" .
echo "📦 Importing reports image into k3s..."
docker save "$REPORTS_IMAGE" | sudo k3s ctr images import -

echo "📄 Applying backend manifests..."
$KUBECTL apply -f k8s/auth.yaml
$KUBECTL apply -f k8s/reports.yaml

if [ "$APPLY_INGRESS" = "1" ]; then
  echo "🌐 Applying ingress..."
  $KUBECTL apply -f k8s/ingress.yaml
fi

echo "♻️ Restarting deployments..."
$KUBECTL rollout restart deploy/auth
$KUBECTL rollout restart deploy/reports

echo "✅ Done"
