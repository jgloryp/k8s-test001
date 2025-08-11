from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class CustomModel(BaseModel):
    """Base model with custom configuration for all API models"""
    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True
    )


class HealthResponse(CustomModel):
    status: str = Field(..., description="Health status")
    timestamp: float = Field(..., description="Current timestamp")
    environment: str = Field(..., description="Current environment")
    version: str = Field(..., description="Application version")
    uptime: float = Field(..., description="Server uptime in seconds")


class ReadinessResponse(CustomModel):
    status: str = Field(..., description="Readiness status")
    timestamp: float = Field(..., description="Current timestamp")


class User(CustomModel):
    id: int = Field(..., ge=1, description="User ID")
    name: str = Field(..., min_length=1, max_length=100, description="User name")
    email: str = Field(..., description="User email address")


class UsersResponse(CustomModel):
    success: bool = Field(True, description="Request success status")
    data: List[User] = Field(..., description="List of users")
    environment: str = Field(..., description="Current environment")


class StatusResponse(CustomModel):
    service: str = Field(..., description="Service name")
    environment: str = Field(..., description="Current environment")
    timestamp: float = Field(..., description="Current timestamp")
    version: str = Field(..., description="Service version")
    features: Dict[str, bool] = Field(..., description="Available features")


class ErrorResponse(CustomModel):
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")


class SimpleResponse(CustomModel):
    message: str = Field(..., description="Response message")