from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import uvicorn
from db.base import engine, Base
from contextlib import asynccontextmanager
from db.models import model
from routers import sign_up, authentication
from authx.exceptions import MissingTokenError, RateLimitExceeded
from fastapi.responses import RedirectResponse, JSONResponse
from redis.asyncio import Redis
from fastapi_mail.email_utils import DefaultChecker

templates = Jinja2Templates(directory="templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


    redis_client = Redis.from_url("redis://localhost:6379/")

    checker = DefaultChecker(
        db_provider="redis",
        redis_client=redis_client
    )

    await checker.fetch_temp_email_domains()
    await checker.init_redis()

    app.state.email_checker = checker

    yield



app = FastAPI(lifespan=lifespan)

app.include_router(sign_up.router)
app.include_router(authentication.router)

@app.exception_handler(MissingTokenError)
def redirector_to_main_page(request: Request, exc: MissingTokenError):
    return RedirectResponse(url="/home", status_code=303)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "status": "error",
            "detail": f"Too many attempts, Try again in {exc.retry_after} seconds."
        }
    )

@app.get("/home")
async def homepage(request: Request):
    return templates.TemplateResponse(request, "main.html")
