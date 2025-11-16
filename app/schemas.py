from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class VerifyRequest(BaseModel):
    init_data: str = Field(..., description="Raw initData string from Telegram WebApp")


class VerifyResponse(BaseModel):
    ok: bool
    reason: Optional[str] = None
    query_id: Optional[str] = None
    auth_date: Optional[int] = None
    user: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    status: str = "ok"

