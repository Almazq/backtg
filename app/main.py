from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import get_bot_token, get_cors_origins, load_environment
from .schemas import HealthResponse, VerifyRequest, VerifyResponse
from .telegram import verify_init_data


# Load environment early
load_environment()

app = FastAPI(title="Telegram Mini App Backend", version="0.1.0")


# CORS
def _setup_cors(app_: FastAPI) -> None:
    allowed_origins: List[str] = get_cors_origins()
    app_.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


_setup_cors(app)


@app.get("/", response_model=HealthResponse)
def root() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/auth/verify", response_model=VerifyResponse)
def auth_verify(payload: VerifyRequest) -> VerifyResponse:
    try:
        bot_token = get_bot_token()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    verification = verify_init_data(payload.init_data, bot_token)
    if not verification.ok:
        return VerifyResponse(
            ok=False,
            reason=verification.reason,
            query_id=verification.query_id,
            auth_date=verification.auth_date,
            user=verification.user,
        )

    return VerifyResponse(
        ok=True,
        reason=None,
        query_id=verification.query_id,
        auth_date=verification.auth_date,
        user=verification.user,
    )


# Optional: allow `python -m app.main` for local runs
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


