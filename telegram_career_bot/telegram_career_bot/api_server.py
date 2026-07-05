import os
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import db.database as db

app = FastAPI(title="Telegram Career Bot API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db.init_db()


class TokenLimitBody(BaseModel):
    token_limit: int


class UserUpdateBody(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    profile: Optional[str] = None
    designation: Optional[str] = None
    token_limit: Optional[int] = None
    status: Optional[str] = None
    onboarding_stage: Optional[str] = None


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok"}


@app.get("/api/users")
def list_users(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1),
    search: Optional[str] = None,
    status: Optional[str] = None,
    onboarding_stage: Optional[str] = None,
    min_tokens: Optional[int] = None,
    sort_by: str = "updated_at",
    order: str = "desc",
) -> dict[str, Any]:
    filters = {
        "search": search,
        "status": status,
        "onboarding_stage": onboarding_stage,
        "min_tokens": min_tokens,
        "sort_by": sort_by,
        "order": order,
    }
    return db.get_users(page=page, limit=limit, filters=filters)


@app.get("/api/users/search")
def search_users(q: str = Query(default="", alias="q"), field: str = "name") -> dict[str, Any]:
    return {"users": db.search_users(q, field=field)}


@app.get("/api/users/{telegram_id}")
def get_user(telegram_id: str) -> dict[str, Any]:
    user = db.get_user(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}


@app.put("/api/users/{telegram_id}")
def update_user(telegram_id: str, payload: UserUpdateBody) -> dict[str, Any]:
    fields = payload.dict(exclude_unset=True)
    if not fields:
        raise HTTPException(status_code=400, detail="No updates provided")
    user = db.update_user(telegram_id, **fields)
    return {"user": user}


@app.delete("/api/users/{telegram_id}")
def delete_user(telegram_id: str) -> dict[str, Any]:
    deleted = db.delete_user(telegram_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"deleted": True}


@app.put("/api/users/bulk-limit")
def bulk_limit(payload: TokenLimitBody) -> dict[str, Any]:
    updated = db.set_token_limit_for_all(payload.token_limit)
    return {"updated": updated, "token_limit": payload.token_limit}


@app.get("/api/stats/dashboard")
def dashboard_stats() -> dict[str, Any]:
    return db.get_stats()


@app.get("/api/stats/token-trends")
def token_trends(days: int = Query(default=30, ge=1)) -> list[dict[str, Any]]:
    return [{"date": "today", "value": 0}] if days else []


@app.get("/api/stats/user-segments")
def user_segments() -> dict[str, Any]:
    return {"segments": []}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api_server:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
