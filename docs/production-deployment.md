# DealVerse OS Production Deployment Guide

This guide provides comprehensive instructions for deploying DealVerse OS to a production Kubernetes environment with full infrastructure, monitoring, and security features.

## 🏗️ Infrastructure Overview

### Architecture Components

- **Kubernetes Cluster**: Container orchestration platform
- **NGINX Ingress Controller**: Load balancing and SSL termination
- **cert-manager**: Automated SSL certificate management
- **Prometheus + Grafana**: Monitoring and alerting
- **Neon PostgreSQL**: Production database
- **Redis**: Caching and session storage
- **S3**: File storage and backups

### Security Features

- SSL/TLS encryption with Let's Encrypt certificates
- Network policies for pod-to-pod communication
- Security headers and CORS configuration
- Container security with non-root users
- Secrets management with Kubernetes secrets

## 📋 Prerequisites

### Required Tools

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify installations
kubectl version --client
helm version
```

### Kubernetes Cluster

- Kubernetes 1.24+ cluster
- At least 3 worker nodes (2 CPU, 4GB RAM each)
- LoadBalancer service support
- Persistent volume support (100GB+ recommended)

### External Services

1. **Neon PostgreSQL Database**
   - Create production database at [neon.com](https://neon.com)
   - Note connection details for configuration

2. **AWS S3 Bucket**
   - Create S3 bucket for file storage
   - Create IAM user with S3 access
   - Note access keys for configuration

3. **Domain Configuration**
   - Register domain (e.g., dealverse.com)
   - Configure DNS records to point to cluster

## 🔧 Configuration

### 1. Update Secrets

Edit `k8s/secrets.yaml` with your production values:

```yaml
stringData:
  # Database Configuration
  DATABASE_URL: "postgresql://user:pass@ep-xxx.us-east-1.aws.neon.tech/dealverse_db"
  
  # JWT Secret (generate strong random key)
  SECRET_KEY: "your-super-secret-key-256-bits-long"
  
  # AWS Credentials
  AWS_ACCESS_KEY_ID: "your-aws-access-key"
  AWS_SECRET_ACCESS_KEY: "your-aws-secret-key"
  
  # API Keys
  OPENROUTER_API_KEY: "your-openrouter-api-key"
  
  # Admin User
  FIRST_SUPERUSER: "admin@yourdomain.com"
  FIRST_SUPERUSER_PASSWORD: "secure-admin-password"
```

### 2. Update ConfigMaps

Edit `k8s/configmap.yaml`:

```yaml
data:
  # Update CORS origins
  BACKEND_CORS_ORIGINS: '["https://app.yourdomain.com", "https://yourdomain.com"]'
  
  # Update S3 bucket
  S3_BUCKET_NAME: "your-s3-bucket-name"
```

### 3. Update Ingress

Edit `k8s/ingress.yaml`:

```yaml
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    - app.yourdomain.com
    secretName: dealverse-tls
  rules:
  - host: api.yourdomain.com
    # ... rest of configuration
```

### 4. Update Certificate Manager

Edit `k8s/cert-manager.yaml`:

```yaml
spec:
  acme:
    email: admin@yourdomain.com  # Your email for Let's Encrypt
```

## 🚀 Deployment

### Automated Deployment

```bash
# Make deployment script executable
chmod +x scripts/deploy-production.sh

# Run full deployment
./scripts/deploy-production.sh

# Or deploy specific components
./scripts/deploy-production.sh monitoring
./scripts/deploy-production.sh database
./scripts/deploy-production.sh backend
```

### Manual Deployment Steps

1. **Create Namespaces**
   ```bash
   kubectl apply -f k8s/namespace.yaml
   ```

2. **Install cert-manager**
   ```bash
   helm repo add jetstack https://charts.jetstack.io
   helm repo update
   helm install cert-manager jetstack/cert-manager \
     --namespace cert-manager \
     --create-namespace \
     --version v1.12.0 \
     --set installCRDs=true
   ```

3. **Install NGINX Ingress**
   ```bash
   helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
   helm install ingress-nginx ingress-nginx/ingress-nginx \
     --namespace ingress-nginx \
     --create-namespace
   ```

4. **Deploy Monitoring**
   ```bash
   kubectl apply -f k8s/monitoring/prometheus.yaml
   kubectl apply -f k8s/monitoring/grafana.yaml
   ```

5. **Deploy Database Configuration**
   ```bash
   kubectl apply -f k8s/database/neon-config.yaml
   ```

6. **Deploy Redis**
   ```bash
   kubectl apply -f k8s/redis.yaml
   ```

7. **Deploy Application**
   ```bash
   kubectl apply -f k8s/configmap.yaml
   kubectl apply -f k8s/secrets.yaml
   kubectl apply -f k8s/backend.yaml
   kubectl apply -f k8s/celery.yaml
   ```

8. **Deploy Ingress**
   ```bash
   kubectl apply -f k8s/cert-manager.yaml
   kubectl apply -f k8s/ingress.yaml
   ```

## 📊 Monitoring and Observability

### Grafana Dashboard

Access Grafana dashboard:

```bash
kubectl port-forward -n dealverse-monitoring svc/grafana 3000:3000
```

- URL: http://localhost:3000
- Username: admin
- Password: (from grafana-secrets)

### Prometheus Metrics

Access Prometheus:

```bash
kubectl port-forward -n dealverse-monitoring svc/prometheus 9090:9090
```

- URL: http://localhost:9090

### Key Metrics to Monitor

- **Application Performance**
  - Request rate and response time
  - Error rate and status codes
  - Database connection pool usage

- **Infrastructure Health**
  - CPU and memory usage
  - Disk space and I/O
  - Network traffic

- **Business Metrics**
  - User registrations and logins
  - Document processing volume
  - API usage patterns

## 🔒 Security Considerations

### SSL/TLS Configuration

- Automatic certificate provisioning with Let's Encrypt
- TLS 1.2+ enforcement
- Strong cipher suites
- HSTS headers

### Network Security

- Network policies restrict pod-to-pod communication
- Ingress controller with rate limiting
- Security headers (CSP, XSS protection, etc.)

### Container Security

- Non-root container execution
- Read-only root filesystems where possible
- Security scanning with Trivy
- Minimal base images

### Secrets Management

- Kubernetes secrets for sensitive data
- Separate secrets for different environments
- Regular secret rotation

## 🔄 CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci-cd.yaml`) provides:

- **Continuous Integration**
  - Automated testing (backend and frontend)
  - Security scanning
  - Code quality checks

- **Continuous Deployment**
  - Automated builds and image publishing
  - Staging environment deployment
  - Production deployment on main branch

### Required GitHub Secrets

```
KUBE_CONFIG_PRODUCTION    # Kubernetes config for production
KUBE_CONFIG_STAGING       # Kubernetes config for staging
GITHUB_TOKEN             # GitHub token for registry access
```

## 🛠️ Maintenance

### Database Backups

Automated daily backups are configured:

```bash
# Check backup job status
kubectl get cronjob database-backup -n dealverse

# Manual backup
kubectl create job --from=cronjob/database-backup manual-backup-$(date +%s) -n dealverse
```

### Scaling

```bash
# Scale backend horizontally
kubectl scale deployment dealverse-backend --replicas=5 -n dealverse

# Scale Celery workers
kubectl scale deployment dealverse-celery-worker --replicas=4 -n dealverse
```

### Updates

```bash
# Update application image
kubectl set image deployment/dealverse-backend backend=ghcr.io/dealverse/backend:v1.2.0 -n dealverse

# Check rollout status
kubectl rollout status deployment/dealverse-backend -n dealverse

# Rollback if needed
kubectl rollout undo deployment/dealverse-backend -n dealverse
```

## 🚨 Troubleshooting

### Common Issues

1. **Pods not starting**
   ```bash
   kubectl describe pod <pod-name> -n dealverse
   kubectl logs <pod-name> -n dealverse
   ```

2. **Database connection issues**
   ```bash
   kubectl exec -it deployment/dealverse-backend -n dealverse -- python -c "
   import asyncpg
   import asyncio
   async def test():
       conn = await asyncpg.connect('$DATABASE_URL')
       print('Database connection successful')
       await conn.close()
   asyncio.run(test())
   "
   ```

3. **SSL certificate issues**
   ```bash
   kubectl describe certificate dealverse-tls -n dealverse
   kubectl describe certificaterequest -n dealverse
   ```

### Health Checks

```bash
# Check all pods
kubectl get pods -n dealverse

# Check services
kubectl get svc -n dealverse

# Check ingress
kubectl get ingress -n dealverse

# Test health endpoint
curl -k https://api.yourdomain.com/health
```

## 📞 Support

For deployment issues or questions:

1. Check the troubleshooting section above
2. Review Kubernetes and application logs
3. Consult the monitoring dashboards
4. Contact the development team with specific error messages and logs
