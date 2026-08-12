from fastapi import APIRouter, Depends, HTTPException, Body, Response, Request, BackgroundTasks, Query
from sqlalchemy.exc import IntegrityError
from ..schemas.register import Register, Admin_OK, PasswordChange
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.base import get_db
from ..db.models.model import users
import bcrypt 
from fastapi.responses import JSONResponse, RedirectResponse
from authx import AuthX, AuthXConfig, TokenPayload, RateLimiter
import os
from dotenv import load_dotenv
from pathlib import Path
from ..utils.utils import user_regulation, create_safe_url_token, decode_url_safe_token
from fastapi.templating import Jinja2Templates
from mailsystem.config import Config 
from mailsystem.mail import create_message, mail
import logging, time
from rich.logging import RichHandler
from datetime import timedelta
from datetime import datetime
from ..schemas.auth import emailSchema


JWT_EXP = timedelta(minutes=Config.JWT_EXPIRY)

file_handler = logging.FileHandler("info.log", encoding="utf-8")
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
))

logging.basicConfig(
    level=logging.INFO,
    format="%(name)s: %(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
    force=True
)

logger = logging.getLogger("mail")

templates = Jinja2Templates(directory="templates")

path = Path(
    __file__
).resolve().parent.parent / ".env"

load_dotenv(path)

config = AuthXConfig(
        JWT_SECRET_KEY=Config.JWT_SECRET_KEY,
        JWT_TOKEN_LOCATION=["headers", "cookies"],
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=15),
        JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=30)
)

auth = AuthX(config=config)

login_rate_limit = RateLimiter(max_requests=5, window=300)

router = APIRouter()

session = Annotated[AsyncSession, Depends(get_db)]

@router.get("/", tags=["Web"])
def general_web_page(request: Request):
    return templates.TemplateResponse(request, "main.html")

@router.get("/signup", tags=["Register"])
def signup_page(request: Request):
    return templates.TemplateResponse(request, "signup.html")

@router.post("/signup", tags=["Register"])
async def sign_up(
    session: session, 
    background: BackgroundTasks, 
    request: Request,
    data: Register = Body(embed=True)
    ) -> JSONResponse:

    domain = data.email.split("@")[-1]
    domain_with_at = "@" + domain

    # checker = request.app.state.email_checker

    # if await checker.is_disposable(data.email):
        # raise HTTPException(
            # status_code=400,
            # detail="Temporary emails are not allowed"
        # ) 

    hashed = bcrypt.hashpw(data.password.encode("utf-8"), bcrypt.gensalt())
    role = 1 # Default value
    '''
    1 is for user👤
    2 is for admin⚡

    ℹ️You can choose if you want to receive only admins here or if you want to make automated registration for administrators you ought
    to use the number "2".

    ⚠️Warning: Always use role value as Integer, string type will be refused!

    ⭐Thanks for attention!
    
    '''
    data_insert = users(
        first_name=data.first_name,
        second_name=data.last_name,
        company_name=data.company_name,
        email=data.email,
        password=hashed.decode("utf-8"),
        job_title=data.job_title,
        role_id=role
    )

    token = create_safe_url_token({"email": data.email})

    link = f"http://{Config.DOMAIN}/api/v1/verify/{token}"

    html_message = f"""
    <h1> Verify your email </h1>
    <p> Please click this <a href="{link}">link</a> to verify your email </p>

    """
    # file_path = Path(__file__).resolve().parent.parent / "C++.cpp"


    message = create_message(
        recipients=[data.email],
        subject="Verification Email",
        body=html_message,
        template_body={
            "first_name": data.first_name,
            "verify_link": link,
            "expires_in": "15 minutes"
        },
        # attachments=[str(file_path), str(file_path2)]
    )

    session.add(data_insert)

    try:
        await session.commit()
        background.add_task(mail.send_message, message, template_name="email_verify.html")

    except IntegrityError:  
        await session.rollback()

        email_check = await user_regulation.get_user_by_email(session, data.email)

        if email_check is None:
            raise HTTPException(
                401,
                "Something went wrong"
            )
        
        is_verified = email_check.email_verified

        if is_verified == False:
            background.add_task(mail.send_message, message, template_name="email_verify.html")
            token = auth.create_access_token(uid=data.email)
            resp = JSONResponse(
                content={
                    "status": "ok", 
                    "redirect": f"/verify_email?email={data.email}"
                }
            )
            auth.set_access_cookies(token, resp)
            return resp

        elif email_check.email_verified == True:
            raise HTTPException(409, "Email existed before")

        else:
            raise HTTPException(
             409,
             "Something went wrong"   
            )

    
    await session.refresh(data_insert)

    jwt_token = auth.create_access_token(uid=data.email, expiry=JWT_EXP)
    resp = JSONResponse(
            status_code=201,
            content={
                "message": "Success"
            }
        )
    auth.set_access_cookies(jwt_token, resp)

    return resp

@router.get("/verify_email", tags=["Email Verification"], dependencies=[Depends(auth.access_token_required)])
def verify_email_webpage(request: Request, email: str = None):
    return templates.TemplateResponse(request, "verify_email.html")

@router.post("/resend_email", dependencies=[Depends(auth.access_token_required)], tags=["Email Verification"])
async def resend_email(background: BackgroundTasks, payload: TokenPayload = Depends(auth.access_token_required)):

    token = create_safe_url_token(
        {"email": payload.sub}
    )

    link = f"http://{Config.DOMAIN}/api/v1/verify/{token}"

    HTML_MESSAGE = f""""
        <h1> Verify your email</h1>
        <p> Click this <a href="{link}" >link </a> in order to verify your account </p1>
    """

    message = create_message(
        recipients=[payload.sub],
        subject="Verification Email",
        template_body={
            "first_name": payload.sub,
            "verify_link": link,
            "expires_in": "15 minutes"
        },
    )

    background.add_task(mail.send_message, message, template_name="email_verify.html")

    return {
        "success": True
    }

@router.get("/api/v1/verify/{token}", tags=["Email Verification"])
async def verify_token(token: str, session: session):
    token_data = decode_url_safe_token(token)

    if token_data:
        email = token_data.get("email")
    else:
        raise HTTPException(404, "Not found Token")

    user = await user_regulation.get_user_by_email(session, email)

    if user is None:
        raise HTTPException(
            404, "Not found user"
        )

    await user_regulation.update_user_email_verification(
        user, 
        {'email_verified': True}, 
        session)

    return JSONResponse(
        status_code=200, 
        content={
            "message": "success"
        }
    )

@router.get("/admin_add", tags=["Administration"], dependencies=[Depends(auth.fresh_token_required)])
def admin_add_dashboard(request: Request):
    return templates.TemplateResponse(request, "admin.html")

@router.get("/password_forgot")
def password_forgot(request: Request):
    return templates.TemplateResponse(request, "password_forgot.html")

@router.post("/v1/password_reset", tags=["Password Change"])
async def password_reset(data: emailSchema, background: BackgroundTasks, session: session):

    result = await user_regulation.get_user_by_email(session, data.email)

    if result is None:
        raise HTTPException(
            404, "Email not found"
        )

    token = create_safe_url_token({"email": data.email})

    link = f"http://{Config.DOMAIN}/v1/confirm/password/reset/{token}"

    html_message = f"""
    <h1> Password Reset</h1>
    <p> Quickly Click this <a href="{link}" >link </a> in order to reset your password </p1>
    """

    message = create_message(
        recipients=[data.email],
        subject="Reset Password",
        body=html_message
    )

    background.add_task(mail.send_message, message)
    
    return {
        "messsage": "success",
    }

@router.get("/v1/confirm/password/reset/{token}", tags=["Password Change"])
async def confirm_password_reset(token: str, session: session, response: Response):

    token_data = decode_url_safe_token(token)

    if token_data:
       email = token_data.get("email")

    else:
        raise HTTPException(
            401, "Unauthorized"
        )

    user = await user_regulation.get_user_by_email(session, email)
    user_mail = user.email

    if user_mail is None:
        raise HTTPException(
            401, "Unauthorized"
        )

    redirect = RedirectResponse(
        url=f"/change_password?token={token}",
        status_code=303
    )

    return redirect 

@router.get("/change_password", tags=["Password Change"])
async def change_password_web(request: Request):
    return templates.TemplateResponse(request, "change_password.html")

@router.put("/v1/change_password",  tags=["Password Change"])
async def change_password(password: PasswordChange, session: session, token: str = Query()):

    token_data = decode_url_safe_token(token)

    if not token_data:
        raise HTTPException(
            401,
            "Invalid or expired reset link"
        )

    email = token_data.get("email")

    hashed_password = bcrypt.hashpw(password.password.encode("utf-8"), bcrypt.gensalt())

    result = await user_regulation.get_user_by_email(session, email)

    if result is None:
        raise HTTPException(
            404, 
            "User not Found"
        )

    result.password = hashed_password.decode("utf-8")
    result.update_at = datetime.now()

    await session.commit()
    await session.refresh(result)

    return {
        "success": "success"
    }


@router.post("/admin_add", tags=["Administration"], dependencies=[Depends(auth.fresh_token_required)])
async def admin_add(session: session, data: Admin_OK):

    hash = bcrypt.hashpw(data.password.encode("utf-8"), bcrypt.gensalt())

    role_id = 2 # 2 is for Admin

    query = users(
        first_name="admin",
        second_name="admin",
        company_name="admin",
        email=data.email,
        password=hash.decode("utf-8"),
        role_id=role_id
    )

    session.add(query)

    try:

        await session.commit()
    
    except IntegrityError:
        raise HTTPException(409, "Admin exists")

    return JSONResponse(
        status_code=200,
        content={
            "message": "success"
        }
    )