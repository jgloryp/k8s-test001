from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, REGISTRY
import time
import os

registry = REGISTRY

def create_prometheus_metrics():
    http_requests_total = Counter(
        'http_requests_total',
        '총 HTTP 요청 수',
        ['method', 'route', 'status_code'],
        registry=registry
    )
    
    http_request_duration = Histogram(
        'http_request_duration_seconds',
        'HTTP 요청 처리 시간 (초)',
        ['method', 'route', 'status_code'],
        buckets=[0.1, 0.5, 1, 2, 5, 10],
        registry=registry
    )
    
    http_connections_active = Gauge(
        'http_connections_active',
        '현재 활성 HTTP 연결 수',
        registry=registry
    )
    
    app_info = Gauge(
        'app_info',
        '애플리케이션 정보',
        ['version', 'environment', 'build_date'],
        registry=registry
    )
    
    app_info.labels(
        version=os.getenv('APP_VERSION', '1.0.0'),
        environment=os.getenv('ENVIRONMENT', 'development'),
        build_date=os.getenv('BUILD_DATE', str(int(time.time())))
    ).set(1)
    
    user_operations_total = Counter(
        'user_operations_total',
        '사용자 작업 총 수',
        ['operation', 'status'],
        registry=registry
    )
    
    database_connection_pool_size = Gauge(
        'database_connection_pool_size',
        '데이터베이스 연결 풀 크기',
        ['state'],
        registry=registry
    )
    
    return {
        'registry': registry,
        'http_requests_total': http_requests_total,
        'http_request_duration': http_request_duration,
        'http_connections_active': http_connections_active,
        'app_info': app_info,
        'user_operations_total': user_operations_total,
        'database_connection_pool_size': database_connection_pool_size
    }