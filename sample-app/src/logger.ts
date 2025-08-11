import winston from 'winston';

// 로그 레벨 및 형식 구성
const logLevel = process.env.LOG_LEVEL || 'info';
const environment = process.env.ENVIRONMENT || 'development';

// JSON 형식으로 구조화된 로깅
const logger = winston.createLogger({
  level: logLevel,
  format: winston.format.combine(
    winston.format.timestamp({
      format: 'YYYY-MM-DD HH:mm:ss'
    }),
    winston.format.errors({ stack: true }),
    winston.format.json(),
    winston.format.printf(({ timestamp, level, message, ...meta }) => {
      return JSON.stringify({
        timestamp,
        level,
        message,
        environment,
        service: 'sample-app',
        ...meta
      });
    })
  ),
  defaultMeta: {
    service: 'sample-app',
    environment: environment
  },
  transports: [
    // 콘솔 출력 (Kubernetes logs)
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    })
  ]
});

// 프로덕션 환경에서는 파일 로깅 추가
if (environment === 'production') {
  logger.add(
    new winston.transports.File({
      filename: '/var/log/app/error.log',
      level: 'error',
      maxsize: 5242880, // 5MB
      maxFiles: 5,
    })
  );
  
  logger.add(
    new winston.transports.File({
      filename: '/var/log/app/combined.log',
      maxsize: 5242880, // 5MB
      maxFiles: 5,
    })
  );
}

// 개발 환경에서는 더 자세한 로깅
if (environment === 'development') {
  logger.level = 'debug';
}

export { logger };