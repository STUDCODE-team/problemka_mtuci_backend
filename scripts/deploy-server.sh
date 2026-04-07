#!/usr/bin/env bash
set -euo pipefail

ENV_FILE=${ENV_FILE:-env/.env.dev}
CONFIGMAP_NAME=${CONFIGMAP_NAME:-problemka-env}
APPLY_INGRESS=${APPLY_INGRESS:-1}
APPLY_DASHBOARD=${APPLY_DASHBOARD:-1}

DASHBOARD_DOMAIN=${DASHBOARD_DOMAIN:-k8s.devapi.problemka-mtuci.tech}
DASHBOARD_USER=${DASHBOARD_USER:-admin}
DASHBOARD_PASSWORD=${DASHBOARD_PASSWORD:-passwd}

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

if [ "$APPLY_DASHBOARD" = "1" ]; then
  echo "📊 Ensuring Kubernetes Dashboard is installed..."
  $KUBECTL apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml

  if [ -n "$DASHBOARD_PASSWORD" ]; then
    if ! $KUBECTL get secret dashboard-basic-auth -n kubernetes-dashboard &>/dev/null; then
      echo "🔐 Creating Dashboard basic auth secret..."
      HTPASSWD_LINE="${DASHBOARD_USER}:$(openssl passwd -apr1 "$DASHBOARD_PASSWORD")"
      printf "%s" "$HTPASSWD_LINE" | $KUBECTL -n kubernetes-dashboard create secret generic dashboard-basic-auth \
        --from-file=auth=/dev/stdin
    else
      echo "🔐 Dashboard basic auth secret already exists, skipping."
    fi
  else
    echo "⚠️  DASHBOARD_PASSWORD is empty; skipping basic auth secret creation."
  fi

  echo "⚙️ Enabling skip-login for Dashboard..."
  if ! $KUBECTL -n kubernetes-dashboard get deployment kubernetes-dashboard -o jsonpath='{.spec.template.spec.containers[0].args}' 2>/dev/null | grep -q "enable-skip-login"; then
    $KUBECTL -n kubernetes-dashboard patch deployment kubernetes-dashboard \
      --type='json' \
      -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--enable-skip-login"}]' \
      2>/dev/null || true
  fi

  echo "🔑 Ensuring Dashboard has cluster-admin permissions..."
  if ! $KUBECTL get clusterrolebinding kubernetes-dashboard-admin &>/dev/null; then
    $KUBECTL create clusterrolebinding kubernetes-dashboard-admin \
      --clusterrole=cluster-admin \
      --serviceaccount=kubernetes-dashboard:kubernetes-dashboard
  fi

  echo "🌐 Applying Dashboard ingress..."
  cat <<EOF_DASH | $KUBECTL apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: kubernetes-dashboard
  namespace: kubernetes-dashboard
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/backend-protocol: "HTTPS"
    nginx.ingress.kubernetes.io/auth-type: "basic"
    nginx.ingress.kubernetes.io/auth-secret: "dashboard-basic-auth"
    nginx.ingress.kubernetes.io/auth-realm: "Authentication Required"
spec:
  rules:
    - host: "$DASHBOARD_DOMAIN"
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: kubernetes-dashboard
                port:
                  number: 443
EOF_DASH
fi

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
