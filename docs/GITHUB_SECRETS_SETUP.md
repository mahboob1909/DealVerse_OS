# GitHub Secrets Configuration Guide

This document explains how to configure the required GitHub repository secrets for the CI/CD pipeline.

## Required Secrets

The GitHub Actions workflow requires the following secrets to be configured in your repository:

### 1. KUBE_CONFIG_STAGING
**Purpose**: Kubernetes configuration for staging environment deployment
**Required for**: Staging deployments on `develop` branch

**How to configure**:
1. Go to your repository on GitHub
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `KUBE_CONFIG_STAGING`
5. Value: Base64-encoded kubeconfig file for your staging Kubernetes cluster

**To get the kubeconfig**:
```bash
# Get your kubeconfig (adjust path as needed)
cat ~/.kube/config | base64 -w 0
```

### 2. KUBE_CONFIG_PRODUCTION
**Purpose**: Kubernetes configuration for production environment deployment
**Required for**: Production deployments on `main` branch

**How to configure**:
1. Go to your repository on GitHub
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `KUBE_CONFIG_PRODUCTION`
5. Value: Base64-encoded kubeconfig file for your production Kubernetes cluster

### 3. SLACK_WEBHOOK
**Purpose**: Slack webhook URL for deployment notifications
**Required for**: Slack notifications after deployments

**How to configure**:
1. Create a Slack webhook in your Slack workspace:
   - Go to https://api.slack.com/apps
   - Create a new app or use existing one
   - Go to "Incoming Webhooks" and activate them
   - Create a new webhook for your desired channel
   - Copy the webhook URL
2. Go to your repository on GitHub
3. Navigate to Settings → Secrets and variables → Actions
4. Click "New repository secret"
5. Name: `SLACK_WEBHOOK`
6. Value: Your Slack webhook URL (e.g., `https://hooks.slack.com/services/...`)

## Current Behavior

If any of these secrets are not configured, the workflow will:

- **Missing KUBE_CONFIG_STAGING**: Skip staging deployment and show a warning message
- **Missing KUBE_CONFIG_PRODUCTION**: Skip production deployment and show a warning message  
- **Missing SLACK_WEBHOOK**: Skip Slack notifications and show a warning message

The workflow will continue to run other jobs (testing, building, security scanning) even if deployment secrets are missing.

## Testing the Configuration

After configuring the secrets:

1. **For staging**: Push to the `develop` branch to trigger staging deployment
2. **For production**: Push to the `main` branch to trigger production deployment
3. **For Slack**: Check your configured Slack channel for deployment notifications

## Security Best Practices

- Use separate kubeconfig files for staging and production with minimal required permissions
- Regularly rotate your Slack webhook URLs
- Monitor secret usage in the Actions tab
- Use environment-specific secrets when possible
- Never commit secrets to your repository

## Troubleshooting

### Common Issues:

1. **Invalid kubeconfig**: Ensure the kubeconfig is properly base64 encoded and has correct cluster access
2. **Slack webhook not working**: Verify the webhook URL is correct and the Slack app has proper permissions
3. **Deployment failures**: Check the Actions logs for specific error messages

### Getting Help:

- Check the Actions tab in your repository for detailed logs
- Verify your Kubernetes cluster is accessible
- Test your Slack webhook manually using curl:
  ```bash
  curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"Test message"}' \
    YOUR_SLACK_WEBHOOK_URL
  ```

## Optional: Local Development

For local development and testing, you can:

1. Use `kubectl` directly with your local kubeconfig
2. Test deployments manually using the k8s manifests in the `k8s/` directory
3. Use Docker Compose for local backend development (see `backend/docker-compose.yml`)