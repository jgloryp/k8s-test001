import express from 'express';
import helmet from 'helmet';
import cors from 'cors';
import compression from 'compression';
import axios from 'axios';
import { createPrometheusMetrics } from './metrics';
import { logger } from './logger';
import { AppError, ErrorHandler, errorHandler, HttpCode, commonErrors } from './errors';

const app = express();
const PORT = process.env.PORT || 3000;
const ENVIRONMENT = process.env.ENVIRONMENT || 'development';
const SAMPLE2_APP_URL = process.env.SAMPLE2_APP_URL || 'http://sample2-app:3000';

// 보안 미들웨어
app.use(helmet());
app.use(cors());
app.use(compression());
app.use(express.json({ limit: '10mb' }));

// Prometheus 메트릭 설정
const metrics = createPrometheusMetrics();

// 요청 로깅 및 메트릭 수집 미들웨어
app.use((req, res, next) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    
    // 메트릭 기록
    metrics.httpRequestDuration
      .labels(req.method, req.route?.path || req.path, res.statusCode.toString())
      .observe(duration / 1000);
    
    metrics.httpRequestsTotal
      .labels(req.method, req.route?.path || req.path, res.statusCode.toString())
      .inc();
    
    // 로그 기록
    logger.info('HTTP Request', {
      method: req.method,
      url: req.url,
      statusCode: res.statusCode,
      duration: `${duration}ms`,
      userAgent: req.get('User-Agent'),
      ip: req.ip
    });
  });
  
  next();
});

// 헬스체크 엔드포인트
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    environment: ENVIRONMENT,
    version: process.env.npm_package_version || '1.0.0',
    uptime: process.uptime()
  });
});

// 준비 상태 체크
app.get('/ready', (req, res) => {
  res.status(200).json({
    status: 'ready',
    timestamp: new Date().toISOString()
  });
});

// 외부 서비스 헬스체크 (sample2-app 확인)
app.get('/health/external', async (req, res) => {
  try {
    const response = await axios.get(`${SAMPLE2_APP_URL}/health`, {
      timeout: 5000
    });
    
    res.status(200).json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      external_services: {
        sample2_app: {
          status: 'healthy',
          url: SAMPLE2_APP_URL,
          response_time: response.headers['response-time'] || 'unknown',
          data: response.data
        }
      }
    });
  } catch (error: any) {
    logger.error('External health check failed', {
      service: 'sample2-app',
      url: SAMPLE2_APP_URL,
      error: error.message
    });
    
    res.status(503).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      external_services: {
        sample2_app: {
          status: 'unhealthy',
          url: SAMPLE2_APP_URL,
          error: error.message
        }
      }
    });
  }
});

// 메트릭 엔드포인트
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', metrics.register.contentType);
  res.end(await metrics.register.metrics());
});

// API 엔드포인트들
app.get('/api/users', (req, res) => {
  const users = [
    { id: 1, name: '홍길동', email: 'hong@example.com' },
    { id: 2, name: '김철수', email: 'kim@example.com' },
    { id: 3, name: '이영희', email: 'lee@example.com' }
  ];
  
  setTimeout(() => {
    res.json({
      success: true,
      data: users,
      environment: ENVIRONMENT
    });
  }, Math.random() * 100); // 응답 시간 시뮬레이션
});

app.get('/api/status', (req, res) => {
  res.json({
    service: 'sample-app',
    environment: ENVIRONMENT,
    timestamp: new Date().toISOString(),
    version: '1.0.0',
    features: {
      monitoring: true,
      logging: true,
      security: true
    }
  });
});

// 에러 시뮬레이션 엔드포인트 (테스트용)
app.get('/api/error', (req, res, next) => {
  const shouldError = Math.random() > 0.7;
  
  if (shouldError) {
    const error = new AppError(
      commonErrors.internalServerError,
      HttpCode.INTERNAL_SERVER_ERROR,
      '시뮬레이션된 에러입니다',
      false // 비운영적 에러
    );
    next(error);
  } else {
    res.json({ message: '정상 응답' });
  }
});

// 404 핸들러
app.use('*', (req, res) => {
  metrics.httpRequestsTotal
    .labels(req.method, 'unknown', '404')
    .inc();
    
  res.status(404).json({
    error: 'Not Found',
    message: '요청한 리소스를 찾을 수 없습니다',
    path: req.originalUrl
  });
});

// 중앙집중식 에러 핸들러 미들웨어
app.use(async (err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  await errorHandler.handleError(err);
  
  const httpCode = err instanceof AppError ? err.httpCode : HttpCode.INTERNAL_SERVER_ERROR;
  
  metrics.httpRequestsTotal
    .labels(req.method, req.route?.path || req.path, httpCode.toString())
    .inc();
  
  // 프로덕션에서는 에러 세부 정보 숨기기
  const message = ENVIRONMENT === 'production' 
    ? '서버 내부 오류가 발생했습니다'
    : err.message;
  
  res.status(httpCode).json({
    error: err instanceof AppError ? err.name : 'Internal Server Error',
    message,
    ...(ENVIRONMENT !== 'production' && { stack: err.stack })
  });
});

// 전역 에러 핸들러 설정
process.on('unhandledRejection', (reason: any) => {
  throw reason;
});

process.on('uncaughtException', async (error: Error) => {
  await errorHandler.handleError(error);
  if (!errorHandler.isTrustedError(error)) {
    process.exit(1);
  }
});

// Graceful shutdown 처리
const server = app.listen(PORT, () => {
  logger.info('Server started', {
    port: PORT,
    environment: ENVIRONMENT,
    nodeVersion: process.version
  });
  
  console.log(`🚀 서버가 포트 ${PORT}에서 실행 중입니다`);
  console.log(`📊 메트릭: http://localhost:${PORT}/metrics`);
  console.log(`🏥 헬스체크: http://localhost:${PORT}/health`);
});

// Graceful shutdown
const gracefulShutdown = (signal: string) => {
  logger.info(`Received ${signal}, shutting down gracefully`);
  
  server.close(() => {
    logger.info('Process terminated gracefully');
    process.exit(0);
  });
  
  // 강제 종료 타이머 (30초)
  setTimeout(() => {
    logger.error('Forceful shutdown after timeout');
    process.exit(1);
  }, 30000);
};

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

export default app;