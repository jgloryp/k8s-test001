import { register, collectDefaultMetrics, Counter, Histogram, Gauge } from 'prom-client';

export function createPrometheusMetrics() {
  // 기본 메트릭 수집 활성화 (CPU, 메모리 등)
  collectDefaultMetrics({ register });

  // HTTP 요청 수 카운터
  const httpRequestsTotal = new Counter({
    name: 'http_requests_total',
    help: '총 HTTP 요청 수',
    labelNames: ['method', 'route', 'status_code'],
    registers: [register]
  });

  // HTTP 요청 지속 시간 히스토그램
  const httpRequestDuration = new Histogram({
    name: 'http_request_duration_seconds',
    help: 'HTTP 요청 처리 시간 (초)',
    labelNames: ['method', 'route', 'status_code'],
    buckets: [0.1, 0.5, 1, 2, 5, 10],
    registers: [register]
  });

  // 활성 연결 수
  const httpConnectionsActive = new Gauge({
    name: 'http_connections_active',
    help: '현재 활성 HTTP 연결 수',
    registers: [register]
  });

  // 애플리케이션 버전 정보
  const appInfo = new Gauge({
    name: 'app_info',
    help: '애플리케이션 정보',
    labelNames: ['version', 'environment', 'build_date'],
    registers: [register]
  });

  // 애플리케이션 정보 설정
  appInfo.set(
    {
      version: process.env.npm_package_version || '1.0.0',
      environment: process.env.ENVIRONMENT || 'development',
      build_date: process.env.BUILD_DATE || new Date().toISOString()
    },
    1
  );

  // 비즈니스 메트릭 예시
  const userOperationsTotal = new Counter({
    name: 'user_operations_total',
    help: '사용자 작업 총 수',
    labelNames: ['operation', 'status'],
    registers: [register]
  });

  const databaseConnectionPool = new Gauge({
    name: 'database_connection_pool_size',
    help: '데이터베이스 연결 풀 크기',
    labelNames: ['state'],
    registers: [register]
  });

  return {
    register,
    httpRequestsTotal,
    httpRequestDuration,
    httpConnectionsActive,
    appInfo,
    userOperationsTotal,
    databaseConnectionPool
  };
}