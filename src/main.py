from contextlib import asynccontextmanager

from authx.exceptions import MissingTokenError, RateLimitExceeded
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi_mail.email_utils import DefaultChecker
from loguru import logger

from .db.base import Base, engine
from .db.seed import seed_roles
from .routers import authentication, sign_up

templates = Jinja2Templates(directory="templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


    # redis_client = Redis.from_url(Config.REDIS_HOST)
    # if you want to add here redis you uncomment variables inside of DefaultChecker()
    checker = DefaultChecker(
        # db_provider="redis",
        # redis_client=redis_client
    )

    try:

        await checker.fetch_temp_email_domains()
    # await checker.init_redis()
    except Exception as e:
        logger.warning(f"Could not fetch temp emails domain: {e}")
    # app.state.email_checker = checker

    await seed_roles()

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
