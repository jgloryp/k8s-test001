import { logger } from './logger';

export enum HttpCode {
  OK = 200,
  CREATED = 201,
  NO_CONTENT = 204,
  BAD_REQUEST = 400,
  UNAUTHORIZED = 401,
  FORBIDDEN = 403,
  NOT_FOUND = 404,
  CONFLICT = 409,
  INTERNAL_SERVER_ERROR = 500,
  SERVICE_UNAVAILABLE = 503,
}

export class AppError extends Error {
  public readonly name: string;
  public readonly httpCode: HttpCode;
  public readonly isOperational: boolean;

  constructor(name: string, httpCode: HttpCode, description: string, isOperational: boolean) {
    super(description);

    Object.setPrototypeOf(this, new.target.prototype);

    this.name = name;
    this.httpCode = httpCode;
    this.isOperational = isOperational;

    Error.captureStackTrace(this);
  }
}

export class ErrorHandler {
  public async handleError(error: Error): Promise<void> {
    await this.logError(error);
    await this.fireMonitoringMetric(error);
  }

  private async logError(error: Error): Promise<void> {
    logger.error('Application error', {
      name: error.name,
      message: error.message,
      stack: error.stack,
      ...(error instanceof AppError && {
        httpCode: error.httpCode,
        isOperational: error.isOperational,
      }),
    });
  }

  private async fireMonitoringMetric(error: Error): Promise<void> {
    // 메트릭 전송 로직 (향후 확장 가능)
    console.warn('Error metric fired:', error.name);
  }

  public isTrustedError(error: Error): boolean {
    if (error instanceof AppError) {
      return error.isOperational;
    }
    return false;
  }
}

export const errorHandler = new ErrorHandler();

export const commonErrors = {
  resourceNotFound: 'RESOURCE_NOT_FOUND',
  validationError: 'VALIDATION_ERROR',
  internalServerError: 'INTERNAL_SERVER_ERROR',
};