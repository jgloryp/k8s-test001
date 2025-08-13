# 배포 가이드

## 사전 준비

### GitLab 설치 및 설정

#### GitLab CE Kubernetes 배포
```bash
# GitLab 네임스페이스 생성
kubectl apply -f k8s/namespaces/gitlab-namespace.yaml

# GitLab Helm 저장소 추가
helm repo add gitlab https://charts.gitlab.io/
helm repo update

# GitLab CE 설치 (최신 stable 버전)
helm upgrade --install gitlab gitlab/gitlab \
  --namespace gitlab \
  --create-namespace \
  --set global.hosts.domain=company.com \
  --set global.hosts.gitlab.name=gitlab.company.com \
  --set certmanager.install=false \
  --set global.ingress.class=nginx \
  --set gitlab-runner.install=true \
  --set global.edition=ce \
  --set global.kas.enabled=false \
  --set global.registry.enabled=true \
  --set gitlab.gitaly.securityContext.runAsUser=1000 \
  --set gitlab.gitaly.securityContext.fsGroup=1000 \
  --timeout=600s \
  --wait

# 설치 상태 확인
kubectl get pods -n gitlab
kubectl get svc -n gitlab

# 초기 root 비밀번호 확인
kubectl get secret -n gitlab gitlab-gitlab-initial-root-password -o jsonpath='{.data.password}' | base64 -d

# GitLab 웹 UI 접속
kubectl port-forward -n gitlab svc/gitlab-webservice-default 8080:8080
```

#### GitLab Repository 생성 및 설정
```bash
# 1. GitLab 웹 인터페이스 접속
# http://localhost:8080 또는 https://gitlab.company.com
# 사용자: root
# 비밀번호: 위에서 확인한 초기 비밀번호

# 2. 새 프로젝트 생성
# - Project name: wb-infrastructure
# - Project URL: http://gitlab.company.com/your-org/wb-infrastructure
# - Visibility Level: Private

# 3. 로컬 저장소와 GitLab 연결
cd /path/to/wb-infrastructure
git init
git remote add origin http://gitlab.company.com/your-org/wb-infrastructure.git

# 4. 브랜치 생성 및 푸시
git add .
git commit -m "Initial commit: WB Infrastructure DevOps platform"
git branch -M main
git push -u origin main

# develop 브랜치 생성
git checkout -b develop
git push -u origin develop
git add .
git commit -m "Initial DevOps infrastructure setup

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
git push -u origin main

# develop 브랜치 생성
git checkout -b develop
git push -u origin develop
```

#### GitLab 접속 및 설정
```bash
# GitLab 서비스 포트포워딩
kubectl port-forward -n gitlab svc/gitlab-webservice-default 8080:8080

# 1. GitLab 웹 인터페이스 접속
# http://localhost:8080 (root/[위에서 확인한 초기 비밀번호])

# 2. 새 프로젝트 생성
# - Project name: wb-infrastructure  
# - Project URL: http://gitlab.company.com/your-org/wb-infrastructure
# - Visibility Level: Private
```

#### GitLab CI/CD 변수 설정
```bash
# GitLab 프로젝트 → Settings → CI/CD → Variables에서 추가:

# Kubernetes 관련
KUBE_CONTEXT=your-k8s-cluster-context
KUBE_CONFIG=<base64-encoded-kubeconfig>

# Container Registry 관련  
CI_REGISTRY=registry.gitlab.com
CI_REGISTRY_USER=gitlab-ci-token
CI_REGISTRY_PASSWORD=<deploy-token>

# 알림 관련
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

#### GitLab Runner (자동 설치됨)
```bash
# GitLab Helm 차트 설치시 Runner도 함께 설치됨
# Runner 상태 확인
kubectl get pods -n gitlab | grep runner

# Runner 등록 토큰 확인
kubectl get secret -n gitlab gitlab-gitlab-runner-secret -o jsonpath='{.data.runner-registration-token}' | base64 -d
```

## 전체 시스템 배포 순서

### 1단계: 클러스터 준비
```bash
# 네임스페이스 생성
kubectl apply -f k8s/namespaces/

# RBAC 구성 적용
kubectl apply -f k8s/rbac/
```

### 2단계: 모니터링 스택 배포

#### Prometheus Operator 설치
```bash
# Helm을 통한 설치 (권장)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=50Gi \
  --set grafana.adminPassword=admin123

# 또는 직접 매니페스트 적용
kubectl apply -f k8s/monitoring/
```

#### 모니터링 구성 확인
```bash
# Prometheus 접근 확인
kubectl port-forward -n monitoring svc/prometheus-operated 9090:9090

# Grafana 접근 확인
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

### 3단계: ArgoCD 설치 및 구성

#### ArgoCD 설치
```bash
# ArgoCD namespace 생성 (이미 생성됨)
kubectl create namespace argocd

# ArgoCD 설치
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 또는 커스텀 구성 적용
kubectl apply -f k8s/argocd/install.yaml
```

#### ArgoCD 초기 설정
```bash
# ArgoCD CLI 설치
curl -sSL -o argocd-linux-amd64 https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
sudo install -m 555 argocd-linux-amd64 /usr/local/bin/argocd

# 초기 비밀번호 확인
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# 포트 포워딩으로 접근
kubectl port-forward -n argocd svc/argocd-server 8080:443

# 로그인 (브라우저에서 https://localhost:8080)
argocd login localhost:8080
```

#### ArgoCD 애플리케이션 등록
```bash
# Test 환경 애플리케이션 등록
kubectl apply -f k8s/argocd/application-test.yaml

# Staging 환경 애플리케이션 등록
kubectl apply -f k8s/argocd/application-staging.yaml
```

### 4단계: 샘플 애플리케이션 배포

#### GitLab에서 프로젝트 설정
1. GitLab에 리포지토리 생성
2. CI/CD 변수 설정:
   - `KUBE_CONTEXT`: Kubernetes 클러스터 컨텍스트
   - `CI_REGISTRY`: 컨테이너 레지스트리 URL
   - `SLACK_WEBHOOK_URL`: Slack 알림용 웹훅

#### 수동 배포 (처음 한 번)
```bash
# Test 환경 배포
helm upgrade --install sample1-app k8s/apps/sample1-app \
  -f k8s/apps/sample1-app/values-test.yaml \
  -n test

# Staging 환경 배포
helm upgrade --install sample1-app k8s/apps/sample1-app \
  -f k8s/apps/sample1-app/values-staging.yaml \
  -n staging
```

### 5단계: 시스템 검증

#### 모니터링 대시보드 확인
```bash
# Grafana 접속 (admin/admin123)
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# 주요 대시보드 확인:
# - Kubernetes 클러스터 오버뷰
# - 애플리케이션 메트릭
# - ArgoCD 배포 현황
```

#### 애플리케이션 상태 확인
```bash
# Pod 상태 확인
kubectl get pods -n test
kubectl get pods -n staging

# 서비스 엔드포인트 확인
kubectl get svc -n test
kubectl get svc -n staging

# ArgoCD에서 동기화 상태 확인
argocd app list
argocd app get sample1-app-test
```

## 일상 운영 작업

### 애플리케이션 업데이트
1. 코드 변경 후 `develop` 브랜치에 푸시
2. GitLab CI/CD가 자동으로 빌드 및 Test 환경 배포
3. Test 검증 완료 후 `main` 브랜치로 머지
4. ArgoCD에서 Staging 배포 수동 승인

### 모니터링 및 알림
- Grafana에서 실시간 메트릭 모니터링
- Slack/이메일로 자동 알림 수신
- 문제 발생시 로그 및 메트릭 분석

### 롤백 절차
```bash
# ArgoCD를 통한 롤백
argocd app rollback sample1-app-staging

# 또는 Helm을 통한 롤백
helm rollback sample1-app -n staging
```