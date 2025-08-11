# Container Image Versions

## Current Versions (Updated: 2025-08-06)

### Platform Versions
| Component | Version | Notes |
|-----------|---------|-------|
| Kubernetes | `1.33.3` | Latest stable (Target cluster version) |

### CI/CD Pipeline Images
| Component | Image | Version |
|-----------|-------|---------|
| Docker | `docker` | `27.3.1` |
| Docker DinD | `docker` | `27.3.1-dind` |
| Node.js | `node` | `22-alpine` |
| Helm | `alpine/helm` | `3.16.3` |
| kubectl | `bitnami/kubectl` | `1.33.3` |
| curl | `curlimages/curl` | `8.11.1` |
| GitLab Runner | `gitlab/gitlab-runner` | `v17.7.0` |

### Security Scanning Tools
| Component | Image | Version |
|-----------|-------|---------|
| Semgrep | `returntocorp/semgrep` | `1.90.0` |
| Trivy | `aquasec/trivy` | `0.58.2` |

### Monitoring Stack
| Component | Image | Version |
|-----------|-------|---------|
| Grafana | `grafana/grafana` | `11.3.1` |

### Application Runtime
| Component | Image | Version |
|-----------|-------|---------|
| Sample App Base | `node` | `22-alpine` |

## Version Update History

### 2025-08-06
- **Kubernetes**: Target version set to `1.33.3` (latest stable)
- **Docker**: `24.0.5` → `27.3.1`
- **Node.js**: `18-alpine` → `22-alpine` 
- **Semgrep**: `latest` → `1.90.0`
- **Trivy**: `latest` → `0.58.2`
- **Helm**: `3.12.0` → `3.16.3`
- **kubectl**: `latest` → `1.33.3` (matches K8s version)
- **curl**: `latest` → `8.11.1`
- **Grafana**: `10.2.0` → `11.3.1`
- **GitLab Runner**: Added `v17.7.0`

## Notes
- All versions updated to latest stable releases as of 2025-08-06
- Removed usage of `:latest` tags for better reproducibility
- Compatible with Kubernetes v1.31.x