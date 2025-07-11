#!/bin/bash

# DealVerse OS Production Deployment Script
# This script deploys DealVerse OS to a Kubernetes cluster with full production infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="dealverse"
MONITORING_NAMESPACE="dealverse-monitoring"
STAGING_NAMESPACE="dealverse-staging"
DOCKER_REGISTRY="ghcr.io"
IMAGE_NAME="dealverse/backend"
IMAGE_TAG="${IMAGE_TAG:-latest}"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    
    # Check if helm is installed
    if ! command -v helm &> /dev/null; then
        log_error "helm is not installed. Please install helm first."
        exit 1
    fi
    
    # Check if we can connect to the cluster
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

create_namespaces() {
    log_info "Creating namespaces..."
    kubectl apply -f k8s/namespace.yaml
    log_success "Namespaces created"
}

install_cert_manager() {
    log_info "Installing cert-manager..."
    
    # Add cert-manager Helm repository
    helm repo add jetstack https://charts.jetstack.io
    helm repo update
    
    # Install cert-manager
    helm upgrade --install cert-manager jetstack/cert-manager \
        --namespace cert-manager \
        --create-namespace \
        --version v1.12.0 \
        --set installCRDs=true \
        --wait
    
    # Wait for cert-manager to be ready
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=cert-manager -n cert-manager --timeout=300s
    
    # Apply cluster issuers
    kubectl apply -f k8s/cert-manager.yaml
    
    log_success "cert-manager installed and configured"
}

install_nginx_ingress() {
    log_info "Installing NGINX Ingress Controller..."
    
    # Add NGINX Ingress Helm repository
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    helm repo update
    
    # Install NGINX Ingress Controller
    helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
        --namespace ingress-nginx \
        --create-namespace \
        --set controller.service.type=LoadBalancer \
        --set controller.metrics.enabled=true \
        --set controller.metrics.serviceMonitor.enabled=true \
        --set controller.podAnnotations."prometheus\.io/scrape"=true \
        --set controller.podAnnotations."prometheus\.io/port"=10254 \
        --wait
    
    # Wait for NGINX Ingress to be ready
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=controller -n ingress-nginx --timeout=300s
    
    log_success "NGINX Ingress Controller installed"
}

deploy_monitoring() {
    log_info "Deploying monitoring stack..."
    
    # Deploy Prometheus
    kubectl apply -f k8s/monitoring/prometheus.yaml
    
    # Deploy Grafana
    kubectl apply -f k8s/monitoring/grafana.yaml
    
    # Wait for monitoring components to be ready
    kubectl wait --for=condition=ready pod -l app=prometheus -n $MONITORING_NAMESPACE --timeout=300s
    kubectl wait --for=condition=ready pod -l app=grafana -n $MONITORING_NAMESPACE --timeout=300s
    
    log_success "Monitoring stack deployed"
}

deploy_database() {
    log_info "Deploying database configuration..."
    
    # Apply database configuration
    kubectl apply -f k8s/database/neon-config.yaml
    
    # Run database migration
    kubectl wait --for=condition=complete job/database-migration -n $NAMESPACE --timeout=300s
    
    log_success "Database configuration deployed and migrations completed"
}

deploy_redis() {
    log_info "Deploying Redis..."
    
    kubectl apply -f k8s/redis.yaml
    
    # Wait for Redis to be ready
    kubectl wait --for=condition=ready pod -l app=dealverse-redis -n $NAMESPACE --timeout=300s
    
    log_success "Redis deployed"
}

deploy_backend() {
    log_info "Deploying backend services..."
    
    # Update image tag in deployment
    sed -i "s|image: dealverse/backend:.*|image: $DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_TAG|g" k8s/backend.yaml
    sed -i "s|image: dealverse/backend:.*|image: $DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_TAG|g" k8s/celery.yaml
    
    # Apply configurations and secrets
    kubectl apply -f k8s/configmap.yaml
    kubectl apply -f k8s/secrets.yaml
    
    # Deploy backend and Celery
    kubectl apply -f k8s/backend.yaml
    kubectl apply -f k8s/celery.yaml
    
    # Wait for deployments to be ready
    kubectl wait --for=condition=available deployment/dealverse-backend -n $NAMESPACE --timeout=600s
    kubectl wait --for=condition=available deployment/dealverse-celery-worker -n $NAMESPACE --timeout=300s
    kubectl wait --for=condition=available deployment/dealverse-celery-beat -n $NAMESPACE --timeout=300s
    
    log_success "Backend services deployed"
}

deploy_ingress() {
    log_info "Deploying ingress configuration..."
    
    kubectl apply -f k8s/ingress.yaml
    
    log_success "Ingress configuration deployed"
}

run_health_checks() {
    log_info "Running health checks..."
    
    # Wait for ingress to get external IP
    log_info "Waiting for ingress to get external IP..."
    sleep 60
    
    # Get ingress IP
    INGRESS_IP=$(kubectl get ingress dealverse-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    
    if [ -z "$INGRESS_IP" ]; then
        log_warning "Ingress IP not available yet. Please check manually later."
        return
    fi
    
    log_info "Ingress IP: $INGRESS_IP"
    
    # Test health endpoint
    if curl -f -k "https://$INGRESS_IP/health" &> /dev/null; then
        log_success "Health check passed"
    else
        log_warning "Health check failed. Service might still be starting up."
    fi
}

print_access_info() {
    log_info "Deployment completed! Access information:"
    echo ""
    echo "🌐 Application URLs:"
    echo "   - Main App: https://app.dealverse.com"
    echo "   - API: https://api.dealverse.com"
    echo "   - Monitoring: https://monitoring.dealverse.com"
    echo ""
    echo "📊 Monitoring Access:"
    echo "   - Grafana: kubectl port-forward -n $MONITORING_NAMESPACE svc/grafana 3000:3000"
    echo "   - Prometheus: kubectl port-forward -n $MONITORING_NAMESPACE svc/prometheus 9090:9090"
    echo ""
    echo "🔧 Useful Commands:"
    echo "   - Check pods: kubectl get pods -n $NAMESPACE"
    echo "   - View logs: kubectl logs -f deployment/dealverse-backend -n $NAMESPACE"
    echo "   - Scale backend: kubectl scale deployment dealverse-backend --replicas=5 -n $NAMESPACE"
    echo ""
    echo "🔐 Security Notes:"
    echo "   - Update secrets in k8s/secrets.yaml before production use"
    echo "   - Configure proper DNS records for your domains"
    echo "   - Review and update SSL certificates"
    echo ""
}

# Main deployment flow
main() {
    log_info "Starting DealVerse OS production deployment..."
    
    check_prerequisites
    create_namespaces
    install_cert_manager
    install_nginx_ingress
    deploy_monitoring
    deploy_database
    deploy_redis
    deploy_backend
    deploy_ingress
    run_health_checks
    print_access_info
    
    log_success "🎉 DealVerse OS production deployment completed successfully!"
}

# Handle script arguments
case "${1:-}" in
    "monitoring")
        deploy_monitoring
        ;;
    "database")
        deploy_database
        ;;
    "backend")
        deploy_backend
        ;;
    "ingress")
        deploy_ingress
        ;;
    "health")
        run_health_checks
        ;;
    *)
        main
        ;;
esac
