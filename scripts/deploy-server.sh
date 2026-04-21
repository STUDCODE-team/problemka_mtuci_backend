#!/usr/bin/env bash
set -euo pipefail

ENV_FILE=${ENV_FILE:-env/.env}
CONFIGMAP_NAME=${CONFIGMAP_NAME:-problemka-env}
NAMESPACE=${NAMESPACE:-dev}
APPLY_INGRESS=${APPLY_INGRESS:-1}

AUTH_IMAGE=${AUTH_IMAGE:-registry.problemka-mtuci.tech/auth:dev}
REPORTS_IMAGE=${REPORTS_IMAGE:-registry.problemka-mtuci.tech/reports:dev}
NOTIFICATION_IMAGE=${NOTIFICATION_IMAGE:-registry.problemka-mtuci.tech/notification:dev}

AUTH_DOCKERFILE=${AUTH_DOCKERFILE:-services/auth/Dockerfile}
REPORTS_DOCKERFILE=${REPORTS_DOCKERFILE:-services/reports/Dockerfile}
NOTIFICATION_DOCKERFILE=${NOTIFICATION_DOCKERFILE:-services/notification/Dockerfile}

KUBECTL="sudo k3s kubectl"

echo "🧱 Ensuring namespace exists..."
$KUBECTL create namespace "$NAMESPACE" --dry-run=client -o yaml | $KUBECTL apply -f -

echo "🧩 Creating/updating env ConfigMap..."
$KUBECTL -n "$NAMESPACE" create configmap "$CONFIGMAP_NAME" \
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

echo "🚧 Building notification image..."
docker build -f "$NOTIFICATION_DOCKERFILE" -t "$NOTIFICATION_IMAGE" .
echo "📦 Importing notification image into k3s..."
docker save "$NOTIFICATION_IMAGE" | sudo k3s ctr images import -

echo "📄 Applying backend manifests..."
$KUBECTL apply -f k8s/services/auth.yaml
$KUBECTL apply -f k8s/services/reports.yaml
$KUBECTL apply -f k8s/services/notification.yaml

if [ "$APPLY_INGRESS" = "1" ]; then
  echo "🌐 Applying ingress..."
  $KUBECTL apply -f k8s/infra/ingress.yaml
fi

echo "📊 Applying monitoring manifests..."
$KUBECTL create namespace monitoring --dry-run=client -o yaml | $KUBECTL apply -f -
$KUBECTL apply -f k8s/monitoring/prometheus.yaml
$KUBECTL apply -f k8s/monitoring/loki.yaml
$KUBECTL apply -f k8s/monitoring/promtail.yaml
$KUBECTL apply -f k8s/monitoring/tempo.yaml
$KUBECTL apply -f k8s/monitoring/grafana.yaml

if [ -n "${GLITCHTIP_SECRET_KEY:-}" ] && [ -n "${GLITCHTIP_DB_PASSWORD:-}" ] && [ -n "${SMTP_PASSWORD:-}" ]; then
  echo "🐛 Creating/updating GlitchTip secret..."
  $KUBECTL -n monitoring create secret generic glitchtip-secret \
    --from-literal=secret-key="${GLITCHTIP_SECRET_KEY}" \
    --from-literal=db-password="${GLITCHTIP_DB_PASSWORD}" \
    --from-literal=database-url="postgresql://glitchtip:${GLITCHTIP_DB_PASSWORD}@glitchtip-db.monitoring.svc.cluster.local:5432/glitchtip" \
    --from-literal=email-url="smtp+tls://no-reply%40problemka-mtuci.tech:${SMTP_PASSWORD}@smtp.mail.ru:587" \
    --dry-run=client -o yaml | $KUBECTL apply -f -

  echo "🐛 Applying GlitchTip manifests..."
  $KUBECTL apply -f k8s/monitoring/glitchtip.yaml
else
  echo "⚠️  Skipping GlitchTip: GLITCHTIP_SECRET_KEY, GLITCHTIP_DB_PASSWORD or SMTP_PASSWORD not set"
fi

echo "♻️ Restarting deployments..."
$KUBECTL -n "$NAMESPACE" rollout restart deploy/auth
$KUBECTL -n "$NAMESPACE" rollout restart deploy/reports
$KUBECTL -n "$NAMESPACE" rollout restart deploy/notification
$KUBECTL -n monitoring rollout restart deploy/prometheus deploy/loki deploy/grafana deploy/tempo
if [ -n "${GLITCHTIP_SECRET_KEY:-}" ]; then
  $KUBECTL -n monitoring rollout restart deploy/glitchtip-web deploy/glitchtip-worker
fi

echo "✅ Done"
