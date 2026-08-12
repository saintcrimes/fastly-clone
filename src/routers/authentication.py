from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from ..db.base import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt 
from ..schemas.auth import auth_log_in
from ..utils.utils import user_regulation, create_safe_url_token, decode_url_safe_token
from .sign_up import auth, templates, TokenPayload, login_rate_limit
from fastapi.responses import JSONResponse, RedirectResponse, Response
from ..schemas.register import Admin_OK
from datetime import timedelta
from fastapi.responses import RedirectResponse
from ..mailsystem.mail import create_message, mail
from ..mailsystem.config import Config


fifteen_minute = timedelta(minutes=5)
thirty_days = timedelta(days=30)


session = Annotated[AsyncSession, Depends(get_db)]

router = APIRouter()

@router.get("/signin", tags=["Sign-in"])
async def sigin_web(request: Request):
    return templates.TemplateResponse(request, "login.html")


@router.post("/signin", tags=["Sign-in"], dependencies=[Depends(login_rate_limit)])   
async def signin(session: session, data: auth_log_in, response: Response, background: BackgroundTasks):
    checker = await user_regulation.check_user_pass(session, data.email, data.password)

    token = auth.create_access_token(uid=data.email)
    refresh = auth.create_refresh_token(uid=data.email)
    auth.set_access_cookies(token, response)
    auth.set_refresh_cookies(refresh, response)

    if checker is False:

        token = create_safe_url_token({"email": data.email})
        
        link = f"http://{Config.DOMAIN}/api/v1/verify/{token}"
        
        html_message = f"""
            <h1> Verify your email </h1>
            <p> Please click this <a href="{link}">link</a> to verify your email </p>
        
            """
        
        message = create_message(
            recipients=[data.email],
            subject="Verification Email",
            body=html_message,
                # attachments=[str(file_path), str(file_path2)]
            )
        
        background.add_task(mail.send_message, message)
        
        return RedirectResponse(
            url="/verify_email",
            status_code=303
        )
    

@router.get("/v1/auth/refresh", dependencies=[Depends(auth.refresh_token_required)])
async def create_refresh_token(response: Response, payload: TokenPayload = Depends(auth.refresh_token_required)):
    token = auth.create_access_token(uid=payload.sub)
    auth.set_access_cookies(token, response)

    return {
        "success": True
    }



@router.get("/admin_login", tags=["Administration"])
def admin_login_webpage(request: Request):
    return templates.TemplateResponse(request, "login.html")

@router.post("/admin_login", tags=["Administration"], description="Admin authentication")
async def admin_login(session: session, admin: Admin_OK):
    query = await user_regulation.admin_check(session, admin.email, admin.password)

    if query == True:
        token = auth.create_access_token(uid=admin.email, fresh=True)
        redirect_response = RedirectResponse(url="/admin_add", status_code=303)
        auth.set_access_cookies(token, redirect_response)
        return redirect_response

    elif query == False:
        return JSONResponse(
            status_code=401,
            content={"message":"Unauthorized"}
        )
    else:
        raise HTTPException(
            409,
            "Oops, Something went wrong!"
        )
    