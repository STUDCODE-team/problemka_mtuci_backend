#!/usr/bin/env bash
# One-time cluster bootstrap: k3s, ingress-nginx, dashboard.
# Run once on a fresh server. Safe to re-run — all steps are idempotent.
set -euo pipefail

DASHBOARD_DOMAIN=${DASHBOARD_DOMAIN:-k8s.devapi.problemka-mtuci.tech}
DASHBOARD_USER=${DASHBOARD_USER:-admin}
DASHBOARD_PASSWORD=${DASHBOARD_PASSWORD:-passwd}

if ! command -v k3s >/dev/null 2>&1; then
  echo "📦 Installing k3s..."
  curl -sfL https://get.k3s.io | sh -s - --disable traefik
fi

KUBECTL="sudo k3s kubectl"

echo "🌐 Installing ingress-nginx..."
$KUBECTL apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.14.2/deploy/static/provider/baremetal/deploy.yaml

echo "🔧 Enabling server-snippet annotations..."
$KUBECTL -n ingress-nginx patch configmap ingress-nginx-controller \
  --type merge \
  -p '{"data":{"allow-snippet-annotations":"true","allow-risky-snippet-annotations":"true"}}'

echo "🔧 Fixing ingress-nginx NodePort to 30080/30443..."
$KUBECTL -n ingress-nginx patch svc ingress-nginx-controller --type='merge' -p '{
  "spec": {
    "type": "NodePort",
    "ports": [
      {"name":"http","port":80,"protocol":"TCP","targetPort":"http","nodePort":30080},
      {"name":"https","port":443,"protocol":"TCP","targetPort":"https","nodePort":30443}
    ]
  }
}'

echo "📊 Installing Kubernetes Dashboard..."
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
fi

echo "⚙️ Enabling skip-login for Dashboard..."
if ! $KUBECTL -n kubernetes-dashboard get deployment kubernetes-dashboard -o jsonpath='{.spec.template.spec.containers[0].args}' 2>/dev/null | grep -q "enable-skip-login"; then
  $KUBECTL -n kubernetes-dashboard patch deployment kubernetes-dashboard \
    --type='json' \
    -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--enable-skip-login"}]' \
    2>/dev/null || true
fi

echo "🔑 Granting Dashboard cluster-admin..."
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

echo "✅ Cluster setup complete"
