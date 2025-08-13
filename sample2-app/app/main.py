from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import time
import random
import os
import asyncio
import httpx
from datetime import datetime
from typing import Optional, List, Dict, Any

from .config import settings
from .metrics import create_prometheus_metrics
from .logger import logger
from .schemas import (
    HealthResponse, ReadinessResponse, User, UsersResponse, 
    StatusResponse, ErrorResponse, SimpleResponse
)
from .exceptions import AppException, SimulatedError, InternalServerError

# OpenAPI 문서 숨기기 (프로덕션 보안)
app_configs = {
    "title": settings.app_name,
    "description": settings.description,
    "version": settings.app_version
}

if settings.environment not in settings.show_docs_environment:
    app_configs["openapi_url"] = None
    app_configs["docs_url"] = None
    app_configs["redoc_url"] = None

app = FastAPI(**app_configs)

# 미들웨어 설정
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

metrics = create_prometheus_metrics()

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    route = getattr(request.scope.get('route'), 'path', request.url.path) if request.scope.get('route') else request.url.path
    
    metrics['http_request_duration'].labels(
        method=request.method,
        route=route,
        status_code=str(response.status_code)
    ).observe(duration)
    
    metrics['http_requests_total'].labels(
        method=request.method,
        route=route,
        status_code=str(response.status_code)
    ).inc()
    
    logger.info(
        "HTTP Request",
        method=request.method,
        url=str(request.url),
        route=route,
        status_code=response.status_code,
        duration_ms=f"{duration * 1000:.2f}ms",
        user_agent=request.headers.get('user-agent'),
        ip=request.client.host if request.client else None
    )
    
    return response

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Application health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        environment=settings.environment,
        version=settings.app_version,
        uptime=time.time()
    )

@app.get("/ready", response_model=ReadinessResponse, tags=["Health"])
async def readiness_check():
    """Application readiness check endpoint"""
    return ReadinessResponse(
        status="ready",
        timestamp=time.time()
    )

@app.get("/health/external", tags=["Health"])
async def external_health_check():
    """외부 서비스 헬스체크 (sample1-app 확인)"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.sample_app_url}/health")
        
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "external_services": {
                "sample_app": {
                    "status": "healthy",
                    "url": settings.sample_app_url,
                    "response_time": response.headers.get('response-time', 'unknown'),
                    "data": response.json()
                }
            }
        }
    except Exception as e:
        logger.error(
            "External health check failed",
            service="sample1-app",
            url=settings.sample_app_url,
            error=str(e)
        )
        
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": time.time(),
                "external_services": {
                    "sample_app": {
                        "status": "unhealthy",
                        "url": settings.sample_app_url,
                        "error": str(e)
                    }
                }
            }
        )

@app.get("/metrics", tags=["Monitoring"])
async def get_metrics():
    """Prometheus metrics endpoint"""
    return Response(
        generate_latest(metrics['registry']),
        media_type=CONTENT_TYPE_LATEST
    )

@app.get("/api/users", response_model=UsersResponse, tags=["API"])
async def get_users():
    """사용자 목록 조회"""
    users_data = [
        {"id": 1, "name": "홍길동", "email": "hong@example.com"},
        {"id": 2, "name": "김철수", "email": "kim@example.com"},
        {"id": 3, "name": "이영희", "email": "lee@example.com"}
    ]
    
    # 비블로킹 비동기 대기 (응답 시간 시뮬레이션)
    await asyncio.sleep(random.uniform(0.01, 0.1))
    
    users = [User(**user) for user in users_data]
    
    return UsersResponse(
        success=True,
        data=users,
        environment=settings.environment
    )

@app.get("/api/status", response_model=StatusResponse, tags=["API"])
async def get_status():
    """서비스 상태 정보"""
    return StatusResponse(
        service=settings.app_name,
        environment=settings.environment,
        timestamp=time.time(),
        version=settings.app_version,
        features={
            "monitoring": True,
            "logging": True,
            "security": True
        }
    )

@app.get("/api/error", response_model=SimpleResponse, tags=["Testing"])
async def simulate_error():
    """에러 시뮬레이션 엔드포인트 (테스트용)"""
    should_error = random.random() > 0.7
    
    if should_error:
        logger.error("Simulated error occurred")
        raise SimulatedError("시뮬레이션된 에러입니다")
    
    return SimpleResponse(message="정상 응답")

# 예외 핸들러 등록
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """애플리케이션 예외 핸들러"""
    route = getattr(request.scope.get('route'), 'path', request.url.path) if request.scope.get('route') else request.url.path
    
    metrics['http_requests_total'].labels(
        method=request.method,
        route=route,
        status_code=str(exc.status_code)
    ).inc()
    
    logger.warning(
        "Application exception",
        error_code=exc.error_code,
        detail=exc.detail,
        url=str(request.url),
        method=request.method,
        is_operational=exc.is_operational
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.detail,
            "detail": exc.detail if settings.environment != "production" else None
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """기본 HTTP 예외 핸들러"""
    route = getattr(request.scope.get('route'), 'path', request.url.path) if request.scope.get('route') else request.url.path
    
    metrics['http_requests_total'].labels(
        method=request.method,
        route=route,
        status_code=str(exc.status_code)
    ).inc()
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP_EXCEPTION",
            "message": exc.detail,
            "path": str(request.url.path)
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """전역 예외 핸들러"""
    route = getattr(request.scope.get('route'), 'path', request.url.path) if request.scope.get('route') else request.url.path
    
    logger.error(
        "Unhandled exception",
        error=str(exc),
        error_type=type(exc).__name__,
        url=str(request.url),
        method=request.method
    )
    
    metrics['http_requests_total'].labels(
        method=request.method,
        route=route,
        status_code='500'
    ).inc()
    
    # 프로덕션에서는 에러 세부 정보 숨기기
    error_detail = str(exc) if settings.environment != "production" else "서버 내부 오류가 발생했습니다"
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": error_detail
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    logger.info(
        "Server starting",
        port=settings.port,
        environment=settings.environment,
        debug=settings.debug
    )
    
    print(f"🚀 서버가 포트 {settings.port}에서 실행 중입니다")
    print(f"📊 메트릭: http://localhost:{settings.port}/metrics")
    print(f"🏥 헬스체크: http://localhost:{settings.port}/health")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower()
    )