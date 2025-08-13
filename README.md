# WB Infrastructure - Blue-Green Deployment System

A simplified Kubernetes-based DevOps platform with independent Blue-Green deployment for two microservices.

## Architecture Overview

- **sample1-app** (Node.js/Express) - Communicates with sample2-app
- **sample2-app** (Python/FastAPI) - Communicates with sample1-app  
- Each service auto-scales to 2 pods using HPA
- Independent Blue-Green deployment for each service
- Health-check communication between services

## File Structure

```
├── sample1-app/                  # Node.js application
├── sample2-app/                 # Python FastAPI application  
├── k8s/
│   ├── apps/
│   │   ├── sample1-app-blue-green/    # Blue-Green Helm chart
│   │   └── sample2-app-blue-green/   # Blue-Green Helm chart
│   ├── argocd/                  # GitOps configurations
│   ├── monitoring/              # Basic monitoring setup
│   └── rbac/                    # Basic RBAC policies
├── scripts/                     # Deployment scripts
└── .gitlab-ci.yml              # CI/CD pipeline
```

## Quick Start

### Prerequisites
- Kubernetes cluster
- Helm 3.x
- kubectl configured

### Deploy Services

```bash
# Deploy sample1-app
helm upgrade --install sample1-app-bg k8s/apps/sample1-app-blue-green

# Deploy sample2-app  
helm upgrade --install sample2-app-bg k8s/apps/sample2-app-blue-green
```

### Health Checks

- **sample1-app**: `http://sample1-app:3000/health`
- **sample1-app external check**: `http://sample1-app:3000/health/external`
- **sample2-app**: `http://sample2-app:3000/health` 
- **sample2-app external check**: `http://sample2-app:3000/health/external`

## Blue-Green Deployment

Each service deploys independently:

```bash
# GitLab CI/CD automatically handles Blue-Green switching
# Manual approval required for production deployment
```

The system:
1. Deploys new version to inactive color (blue/green)
2. Health checks the new version
3. Switches traffic to new version
4. Keeps old version as rollback option

## Auto-scaling

Both services auto-scale between 2-4 pods based on:
- CPU utilization (70% threshold)
- Memory utilization (80% threshold)

## Monitoring

Basic Prometheus metrics are collected from:
- `/metrics` endpoints on both services
- Kubernetes cluster metrics
- Application health status

## Development

### Local Testing

```bash
# Start sample1-app
cd sample1-app
npm install
npm run dev

# Start sample2-app  
cd sample2-app
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Environment Variables

**sample1-app:**
- `SAMPLE2_APP_URL`: URL to sample2-app service

**sample2-app:**
- `SAMPLE_APP_URL`: URL to sample1-app service

## CI/CD Pipeline

The GitLab CI/CD pipeline:

1. **Build** - Creates Docker images
2. **Test** - Runs unit tests and linting
3. **Deploy** - Blue-Green deployment (manual approval)

Each service deploys independently when its code changes.

