from fastapi import HTTPException, status
from typing import Any, Dict, Optional


class AppException(HTTPException):
    """Base application exception with structured error information"""
    
    def __init__(
        self, 
        status_code: int,
        detail: str,
        error_code: str,
        is_operational: bool = True,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code
        self.is_operational = is_operational


class ValidationError(AppException):
    def __init__(self, detail: str = "Validation failed"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="VALIDATION_ERROR",
            is_operational=True
        )


class NotFoundError(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="NOT_FOUND",
            is_operational=True
        )


class InternalServerError(AppException):
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="INTERNAL_SERVER_ERROR",
            is_operational=False
        )


class SimulatedError(AppException):
    def __init__(self, detail: str = "시뮬레이션된 에러입니다"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="SIMULATED_ERROR",
            is_operational=False
        )