# Test001 Infrastructure DevOps 플랫폼

두 개의 마이크로서비스를 위한 독립적인 Blue-Green 배포가 포함된 간소화된 Kubernetes 기반 DevOps 플랫폼입니다.

## 아키텍처 개요

- **sample1-app** (Node.js/Express) - sample2-app과 통신
- **sample2-app** (Python/FastAPI) - sample1-app과 통신  
- 각 서비스는 HPA를 사용하여 2개 파드로 자동 확장
- 각 서비스별 독립적인 Blue-Green 배포
- 서비스 간 헬스체크 통신

## 파일 구조

```
├── sample1-app/                  # Node.js 애플리케이션
├── sample2-app/                 # Python FastAPI 애플리케이션  
├── k8s/
│   ├── apps/
│   │   ├── sample1-app-blue-green/    # Blue-Green Helm 차트
│   │   └── sample2-app-blue-green/   # Blue-Green Helm 차트
│   ├── argocd/                  # GitOps 구성
│   ├── monitoring/              # 기본 모니터링 설정
│   └── rbac/                    # 기본 RBAC 정책
├── scripts/                     # 배포 스크립트
└── .gitlab-ci.yml              # CI/CD 파이프라인
```

## 빠른 시작

### 사전 요구사항
- Kubernetes 클러스터
- Helm 3.x
- kubectl 구성 완료

### 서비스 배포

```bash
# sample1-app 배포
helm upgrade --install sample1-app-bg k8s/apps/sample1-app-blue-green

# sample2-app 배포  
helm upgrade --install sample2-app-bg k8s/apps/sample2-app-blue-green
```

### 헬스체크

- **sample1-app**: `http://sample1-app:3000/health`
- **sample1-app 외부 체크**: `http://sample1-app:3000/health/external`
- **sample2-app**: `http://sample2-app:3000/health` 
- **sample2-app 외부 체크**: `http://sample2-app:3000/health/external`

## Blue-Green 배포

각 서비스는 독립적으로 배포됩니다:

```bash
# GitLab CI/CD가 자동으로 Blue-Green 전환 처리
# 프로덕션 배포에는 수동 승인 필요
```

시스템 동작 방식:
1. 비활성 색상(blue/green)에 새 버전 배포
2. 새 버전 헬스체크 수행
3. 새 버전으로 트래픽 전환
4. 이전 버전을 롤백 옵션으로 유지

## 자동 확장

두 서비스 모두 다음 기준에 따라 2-4개 파드 사이에서 자동 확장:
- CPU 사용률 (70% 임계값)
- 메모리 사용률 (80% 임계값)

## 모니터링

다음으로부터 기본 Prometheus 메트릭 수집:
- 두 서비스의 `/metrics` 엔드포인트
- Kubernetes 클러스터 메트릭
- 애플리케이션 헬스 상태

## 개발

### 로컬 테스트

```bash
# sample1-app 시작
cd sample1-app
npm install
npm run dev

# sample2-app 시작  
cd sample2-app
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 환경 변수

**sample1-app:**
- `SAMPLE2_APP_URL`: sample2-app 서비스 URL

**sample2-app:**
- `SAMPLE_APP_URL`: sample1-app 서비스 URL

## CI/CD 파이프라인

GitLab CI/CD 파이프라인:

1. **빌드** - Docker 이미지 생성
2. **테스트** - 단위 테스트 및 린팅 실행
3. **배포** - Blue-Green 배포 (수동 승인)

각 서비스는 코드 변경 시 독립적으로 배포됩니다.

