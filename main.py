from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi_limiter import FastAPILimiter
from starlette import status

from src.settings import settings
from src.routes import auth, contacts, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    r = await redis.Redis(
        host=settings.redis.host,
        port=settings.redis.port,
        db=0,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(r)
    yield

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def redirect_to_docs():
    return RedirectResponse("/docs", status_code=status.HTTP_302_FOUND)


app.include_router(auth.router)
app.include_router(contacts.router)
app.include_router(users.router)
