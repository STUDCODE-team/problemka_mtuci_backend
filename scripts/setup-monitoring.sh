#!/usr/bin/env bash
# One-time monitoring bootstrap: Grafana (and its ingress). Safe to re-run.
set -euo pipefail

KUBECTL="sudo k3s kubectl"

GRAFANA_ADMIN_USER=${GRAFANA_ADMIN_USER:-admin}
GRAFANA_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:-}

echo "🧱 Ensuring monitoring namespace exists..."
$KUBECTL create namespace monitoring --dry-run=client -o yaml | $KUBECTL apply -f -

echo "🔐 Ensuring Grafana admin secret exists..."
if ! $KUBECTL -n monitoring get secret grafana-admin &>/dev/null; then
  if [ -z "${GRAFANA_ADMIN_PASSWORD}" ]; then
    GRAFANA_ADMIN_PASSWORD="$(openssl rand -base64 36 | tr -d '\n' | tr '+/' '-_' | cut -c1-32)"
  fi

  $KUBECTL -n monitoring create secret generic grafana-admin \
    --from-literal=admin-user="$GRAFANA_ADMIN_USER" \
    --from-literal=admin-password="$GRAFANA_ADMIN_PASSWORD"

  unset GRAFANA_ADMIN_PASSWORD
  echo "ℹ️  Grafana admin password is stored in secret monitoring/grafana-admin."
else
  echo "🔐 Grafana admin secret already exists, skipping."
fi

echo "📈 Applying Grafana manifests..."
$KUBECTL apply -f k8s/grafana.yaml

echo "✅ Monitoring setup complete"
