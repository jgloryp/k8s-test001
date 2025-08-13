#!/bin/bash
# 시스템 전체 검증 스크립트
# 모든 구성 요소의 유효성을 검사하고 설정 일관성을 확인

set -euo pipefail

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 로깅 함수
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_check() { echo -e "${BLUE}[CHECK]${NC} $1"; }

# 전역 변수
VALIDATION_ERRORS=0
VALIDATION_WARNINGS=0

# 오류 카운터 함수
increment_error() { ((VALIDATION_ERRORS++)); }
increment_warning() { ((VALIDATION_WARNINGS++)); }

# 파일 존재 확인 함수
check_file_exists() {
    local file="$1"
    local description="$2"
    
    if [[ -f "$file" ]]; then
        echo "✅ $description"
        return 0
    else
        echo "❌ $description 누락: $file"
        increment_error
        return 1
    fi
}

# YAML 유효성 검사 함수
validate_yaml() {
    local file="$1"
    
    if command -v kubectl &> /dev/null; then
        if kubectl apply --dry-run=client -f "$file" &> /dev/null; then
            echo "✅ YAML 유효: $(basename "$file")"
        else
            echo "❌ YAML 오류: $(basename "$file")"
            increment_error
        fi
    else
        log_warn "kubectl이 없어 YAML 검증을 건너뜁니다"
        increment_warning
    fi
}

# 핵심 파일 구조 검증
validate_core_structure() {
    log_check "핵심 파일 구조 검증"
    
    # 루트 파일들
    check_file_exists ".gitlab-ci.yml" "GitLab CI/CD 메인 파이프라인"
    check_file_exists "README.md" "프로젝트 README"
    check_file_exists "CLAUDE.md" "Claude 작업 기록"
    
    # 스크립트 파일들
    local scripts=(
        "scripts/deploy.sh:메인 배포 스크립트"
        "scripts/deploy-independent-blue-green.sh:독립적 Blue-Green 배포 스크립트"
        "scripts/health-check.sh:헬스체크 스크립트"
        "scripts/cleanup.sh:정리 스크립트"
        "scripts/validate-system.sh:시스템 검증 스크립트"
    )
    
    for script_info in "${scripts[@]}"; do
        file="${script_info%:*}"
        desc="${script_info#*:}"
        check_file_exists "$file" "$desc"
    done
    
    # 디렉터리 구조
    local dirs=(
        "k8s/namespaces:네임스페이스 구성"
        "k8s/rbac:RBAC 및 보안 정책"
        "k8s/monitoring:모니터링 시스템"
        "k8s/argocd:ArgoCD 구성"
        "k8s/apps:애플리케이션 매니페스트"
        "sample1-app:Node.js 샘플 애플리케이션"
        "sample2-app:Python FastAPI 샘플 애플리케이션"
        "docs:문서 및 가이드"
        "packages:Helm 차트 패키지"
    )
    
    for dir_info in "${dirs[@]}"; do
        dir="${dir_info%:*}"
        desc="${dir_info#*:}"
        if [[ -d "$dir" ]]; then
            echo "✅ $desc 디렉터리 존재"
        else
            echo "❌ $desc 디렉터리 누락: $dir"
            increment_error
        fi
    done
}

# Helm 차트 검증
validate_helm_charts() {
    log_check "Helm 차트 검증"
    
    local charts=(
        "k8s/apps/sample1-app"
        "k8s/apps/sample2-app" 
        "k8s/apps/sample1-app-blue-green"
        "k8s/apps/sample2-app-blue-green"
    )
    
    for chart in "${charts[@]}"; do
        if [[ -f "$chart/Chart.yaml" ]]; then
            echo "✅ Helm 차트 존재: $(basename "$chart")"
            
            # Chart.yaml 템플릿 렌더링 테스트
            if command -v helm &> /dev/null; then
                if helm template test "$chart" &> /dev/null; then
                    echo "✅ Helm 템플릿 렌더링 성공: $(basename "$chart")"
                else
                    echo "❌ Helm 템플릿 렌더링 실패: $(basename "$chart")"
                    increment_error
                fi
            else
                log_warn "helm이 없어 템플릿 검증을 건너뜁니다"
                increment_warning
            fi
        else
            echo "❌ Helm 차트 누락: $chart"
            increment_error
        fi
    done
}

# ArgoCD 애플리케이션 검증
validate_argocd_apps() {
    log_check "ArgoCD 애플리케이션 검증"
    
    local apps=(
        "k8s/argocd/application-test.yaml:기본 Test 환경"
        "k8s/argocd/application-staging.yaml:기본 Staging 환경"
        "k8s/argocd/application-sample1-app-blue-green-test.yaml:sample1-app Blue-Green Test"
        "k8s/argocd/application-sample1-app-blue-green-staging.yaml:sample1-app Blue-Green Staging"
        "k8s/argocd/application-sample2-app-blue-green-test.yaml:sample2-app Blue-Green Test"
        "k8s/argocd/application-sample2-app-blue-green-staging.yaml:sample2-app Blue-Green Staging"
    )
    
    for app_info in "${apps[@]}"; do
        file="${app_info%:*}"
        desc="${app_info#*:}"
        check_file_exists "$file" "ArgoCD 애플리케이션: $desc"
        [[ -f "$file" ]] && validate_yaml "$file"
    done
}

# 네임스페이스 검증
validate_namespaces() {
    log_check "네임스페이스 구성 검증"
    
    local namespaces=(
        "k8s/namespaces/test-namespace.yaml:Test 환경"
        "k8s/namespaces/staging-namespace.yaml:Staging 환경"
        "k8s/namespaces/monitoring-namespace.yaml:모니터링"
        "k8s/namespaces/argocd-namespace.yaml:ArgoCD"
        "k8s/namespaces/gitlab-namespace.yaml:GitLab"
    )
    
    for ns_info in "${namespaces[@]}"; do
        file="${ns_info%:*}"
        desc="${ns_info#*:}"
        check_file_exists "$file" "네임스페이스: $desc"
        [[ -f "$file" ]] && validate_yaml "$file"
    done
}

# 보안 구성 검증
validate_security() {
    log_check "보안 구성 검증"
    
    local security_files=(
        "k8s/rbac/service-accounts.yaml:서비스 계정"
        "k8s/rbac/cluster-roles.yaml:클러스터 역할"
        "k8s/rbac/role-bindings.yaml:역할 바인딩"
        "k8s/rbac/network-policies.yaml:네트워크 정책"
        "k8s/rbac/pod-security-standards.yaml:Pod 보안 표준"
    )
    
    for security_info in "${security_files[@]}"; do
        file="${security_info%:*}"
        desc="${security_info#*:}"
        check_file_exists "$file" "보안 구성: $desc"
        [[ -f "$file" ]] && validate_yaml "$file"
    done
}

# 모니터링 구성 검증
validate_monitoring() {
    log_check "모니터링 구성 검증"
    
    local monitoring_files=(
        "k8s/monitoring/prometheus-operator.yaml:Prometheus Operator"
        "k8s/monitoring/servicemonitor.yaml:ServiceMonitor"
        "k8s/monitoring/alerting-rules.yaml:알림 규칙"
        "k8s/monitoring/alertmanager.yaml:Alertmanager"
        "k8s/monitoring/grafana.yaml:Grafana"
        "k8s/monitoring/grafana-config.yaml:Grafana 구성"
    )
    
    for monitoring_info in "${monitoring_files[@]}"; do
        file="${monitoring_info%:*}"
        desc="${monitoring_info#*:}"
        check_file_exists "$file" "모니터링: $desc"
        [[ -f "$file" ]] && validate_yaml "$file"
    done
}

# 애플리케이션 구성 검증
validate_applications() {
    log_check "애플리케이션 구성 검증"
    
    # sample1-app 검증
    check_file_exists "sample1-app/Dockerfile" "sample1-app Dockerfile"
    check_file_exists "sample1-app/package.json" "sample1-app package.json"
    check_file_exists "sample1-app/src/server.ts" "sample1-app 메인 서버"
    
    # sample2-app 검증
    check_file_exists "sample2-app/Dockerfile" "sample2-app Dockerfile"
    check_file_exists "sample2-app/requirements.txt" "sample2-app requirements"
    check_file_exists "sample2-app/app/main.py" "sample2-app 메인 앱"
}

# 문서 검증
validate_documentation() {
    log_check "문서화 검증"
    
    local docs=(
        "docs/architecture.md:아키텍처 문서"
        "docs/deployment-guide.md:배포 가이드"
        "docs/independent-blue-green-deployment.md:독립적 Blue-Green 배포 가이드"
        "docs/troubleshooting.md:문제 해결 가이드"
        "docs/best-practices.md:모범 사례"
        "docs/configuration-guide.md:구성 가이드"
        "docs/versions.md:버전 정보"
    )
    
    for doc_info in "${docs[@]}"; do
        file="${doc_info%:*}"
        desc="${doc_info#*:}"
        check_file_exists "$file" "문서: $desc"
    done
}

# 권한 검증
validate_permissions() {
    log_check "스크립트 실행 권한 검증"
    
    local scripts=(
        "scripts/deploy.sh"
        "scripts/deploy-independent-blue-green.sh"
        "scripts/health-check.sh"
        "scripts/cleanup.sh"
        "scripts/validate-system.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [[ -f "$script" ]]; then
            if [[ -x "$script" ]]; then
                echo "✅ 실행 권한 OK: $(basename "$script")"
            else
                echo "⚠️  실행 권한 없음: $(basename "$script")"
                chmod +x "$script" 2>/dev/null && echo "✅ 실행 권한 추가됨" || (echo "❌ 권한 추가 실패" && increment_error)
            fi
        fi
    done
}

# 종속성 검증
validate_dependencies() {
    log_check "시스템 종속성 검증"
    
    local tools=(
        "kubectl:Kubernetes CLI"
        "helm:Helm 패키지 매니저"
        "docker:Docker 컨테이너 엔진"
    )
    
    for tool_info in "${tools[@]}"; do
        tool="${tool_info%:*}"
        desc="${tool_info#*:}"
        
        if command -v "$tool" &> /dev/null; then
            version=$("$tool" version --short 2>/dev/null || "$tool" --version 2>/dev/null || echo "Unknown")
            echo "✅ $desc 설치됨: $version"
        else
            echo "⚠️  $desc 미설치"
            increment_warning
        fi
    done
}

# 메인 검증 함수
run_validation() {
    echo "🔍 WB Infrastructure 시스템 검증을 시작합니다..."
    echo "=================================================="
    
    validate_core_structure
    echo ""
    
    validate_helm_charts
    echo ""
    
    validate_argocd_apps
    echo ""
    
    validate_namespaces
    echo ""
    
    validate_security
    echo ""
    
    validate_monitoring
    echo ""
    
    validate_applications
    echo ""
    
    validate_documentation
    echo ""
    
    validate_permissions
    echo ""
    
    validate_dependencies
    echo ""
    
    echo "=================================================="
    
    # 결과 요약
    if [[ $VALIDATION_ERRORS -eq 0 ]]; then
        log_info "✅ 모든 검증 통과! ($VALIDATION_WARNINGS개 경고)"
        echo ""
        log_info "🚀 시스템이 배포 준비 완료되었습니다."
        return 0
    else
        log_error "❌ $VALIDATION_ERRORS개 오류, $VALIDATION_WARNINGS개 경고 발견"
        echo ""
        log_error "🔧 오류를 수정한 후 다시 실행하세요."
        return 1
    fi
}

# 스크립트 실행
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    run_validation "$@"
fi