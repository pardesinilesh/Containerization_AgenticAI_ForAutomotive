# Kubernetes Deployment Guide

## Prerequisites

- Kubernetes cluster (1.24+) with kubectl configured
- Helm 3.x (optional but recommended)
- Container registry (Docker Hub, Azure ACR, or private)
- Argo CD 2.x installed in cluster
- PostgreSQL accessible to cluster

## Step 1: Create Namespace and RBAC

```bash
# Apply namespace and RBAC setup
kubectl apply -f kubernetes/rbac.yaml

# Verify
kubectl get namespace automotive-tools
kubectl get serviceaccount -n automotive-tools
```

## Step 2: Setup Storage

### Option A: Dynamic PV (Recommended for cloud)

```bash
# Verify storage class exists
kubectl get storageclass

# If not, create simple local storage
kubectl apply -f - <<EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
EOF
```

### Option B: Manual PV (For on-premise)

```bash
kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolume
metadata:
  name: auto-tools-pv
spec:
  capacity:
    storage: 100Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: /mnt/automotive-tools
EOF
```

## Step 3: Setup Container Registry Credentials

```bash
# Create docker registry secret
kubectl create secret docker-registry registry-creds \
  --docker-server=$REGISTRY_URL \
  --docker-username=$REGISTRY_USER \
  --docker-password=$REGISTRY_PASSWORD \
  --docker-email=$REGISTRY_EMAIL \
  -n automotive-tools

# Patch default service account
kubectl patch serviceaccount default \
  -p '{"imagePullSecrets": [{"name": "registry-creds"}]}' \
  -n automotive-tools
```

## Step 4: Deploy PostgreSQL (Optional - if not externally managed)

```bash
# Using Helm (recommended)
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install postgresql bitnami/postgresql \
  --set auth.postgresPassword=postgres \
  --set auth.database=automotive \
  --set primary.persistence.size=50Gi \
  -n automotive-tools

# Or using manifest
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-init
  namespace: automotive-tools
data:
  init.sql: |
    CREATE DATABASE automotive;
    $(cat database/schema.sql)
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: automotive-tools
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: automotive
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 50Gi
EOF
```

## Step 5: Deploy ConfigMaps

```bash
# Deploy app configuration
kubectl create configmap app-config \
  --from-file=config/environments/production.yaml \
  --from-file=config/tools/ \
  -n automotive-tools

# Verify
kubectl get configmap -n automotive-tools
```

## Step 6: Deploy Secrets

```bash
# Create secrets
kubectl create secret generic app-secrets \
  --from-literal=anthropic-api-key=$ANTHROPIC_API_KEY \
  --from-literal=db-password=$DB_PASSWORD \
  -n automotive-tools

# Verify
kubectl get secrets -n automotive-tools
```

## Step 7: Deploy Application

### Option A: Using kubectl

```bash
# Deploy
kubectl apply -f kubernetes/deployment.yaml \
  -f kubernetes/service.yaml \
  -f kubernetes/pvc.yaml \
  -f kubernetes/configmap.yaml \
  -n automotive-tools

# Verify rollout
kubectl rollout status deployment/automotive-trace32 \
  -n automotive-tools

# Check logs
kubectl logs -f deployment/automotive-trace32 \
  -n automotive-tools
```

### Option B: Using Argo CD

```bash
# Install Argo CD if needed
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Create Argo CD Application
kubectl apply -f argo-cd/application.yaml

# Monitor
argocd app get automotive-trace32
argocd app logs automotive-trace32 -f

# Argo CD UI
kubectl port-forward svc/argocd-server -n argocd 9443:443
# Access: https://localhost:9443 (admin/password in secret)
```

## Step 8: Verify Deployment

```bash
# Check deployment status
kubectl get deployments -n automotive-tools
kubectl get pods -n automotive-tools
kubectl get services -n automotive-tools

# Check specific pod
kubectl describe pod <pod-name> -n automotive-tools

# Test service connectivity
kubectl run -it --rm debug --image=alpine \     --restart=Never -n automotive-tools -- \
    wget -qO- http://automotive-trace32-service:8080/health
```

## Step 9: Setup Ingress (Optional)

```bash
# Using NGINX Ingress
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: automotive-trace32-ingress
  namespace: automotive-tools
spec:
  ingressClassName: nginx
  rules:
  - host: trace32.automotive.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: automotive-trace32-service
            port:
              number: 8080
  tls:
  - hosts:
    - trace32.automotive.local
    secretName: trace32-tls
EOF
```

## Step 10: Setup Monitoring (Optional)

```bash
# Install Prometheus operator
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  -n automotive-tools

# Add service monitor
kubectl apply -f - <<EOF
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: automotive-trace32
  namespace: automotive-tools
spec:
  selector:
    matchLabels:
      app: automotive-trace32
  endpoints:
  - port: http
    interval: 30s
EOF
```

## Scaling

### Horizontal Scaling

```bash
# Scale manually
kubectl scale deployment automotive-trace32 \
  --replicas=5 \
  -n automotive-tools

# Use HPA for auto-scaling
kubectl apply -f - <<EOF
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: automotive-trace32-hpa
  namespace: automotive-tools
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: automotive-trace32
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
EOF
```

## Upgrades & Rollbacks

### Deploy New Version

```bash
# Update deployment image
kubectl set image deployment/automotive-trace32 \
  automotive-trace32=registry.io/automotive-trace32:v2.0 \
  -n automotive-tools

# Monitor rollout
kubectl rollout status deployment/automotive-trace32 \
  -n automotive-tools

# View rollout history
kubectl rollout history deployment/automotive-trace32 \
  -n automotive-tools
```

### Rollback

```bash
# Rollback to previous version
kubectl rollout undo deployment/automotive-trace32 \
  -n automotive-tools

# Rollback to specific revision
kubectl rollout undo deployment/automotive-trace32 \
  --to-revision=2 \
  -n automotive-tools
```

## Maintenance

### Backup Database

```bash
# Port forward to postgres
kubectl port-forward svc/postgres 5432:5432 \
  -n automotive-tools &

# Backup
PGPASSWORD=postgres pg_dump -h localhost \
  -U postgres automotive > backup.sql

# Kill port-forward
killall kubectl
```

### Database Restore

```bash
# Port forward
kubectl port-forward svc/postgres 5432:5432 \
  -n automotive-tools &

# Restore
PGPASSWORD=postgres psql -h localhost \
  -U postgres automotive < backup.sql

killall kubectl
```

### Pod Logs

```bash
# Current logs
kubectl logs <pod-name> -n automotive-tools

# Last 100 lines
kubectl logs --tail=100 <pod-name> -n automotive-tools

# Follow logs
kubectl logs -f <pod-name> -n automotive-tools

# Previous logs (if pod crashed)
kubectl logs <pod-name> --previous \
  -n automotive-tools
```

## Cleanup

```bash
# Delete deployment
kubectl delete deployment automotive-trace32 \
  -n automotive-tools

# Delete namespace (careful: removes everything)
kubectl delete namespace automotive-tools

# Delete Argo CD app
kubectl delete application automotive-trace32 \
  -n argocd
```

---

For production deployments, also consider:
- Resource quotas
- Network policies
- Pod security policies
- Certificate management
- Backup strategies
- Disaster recovery
