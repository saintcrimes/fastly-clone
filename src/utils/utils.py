from sqlalchemy import select
from db.models import model
from fastapi import HTTPException
import bcrypt
import logging
from fastapi.responses import JSONResponse
from itsdangerous import URLSafeTimedSerializer
from mailsystem.config import Config
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.model import users

serializer = URLSafeTimedSerializer(
    secret_key=Config.JWT_SECRET_KEY,
    salt="email-configuration"
)

class user_service:
    @staticmethod
    async def check_user_pass(session, email, password):


        query = await session.execute(select(model.users).where(model.users.email == email))
        result = query.scalar_one_or_none()

        if result is None:
            raise HTTPException(404, "Wrong email or password")   
        
        is_correct = bcrypt.checkpw(password.encode("utf-8"), result.password.encode("utf-8"))

        if is_correct is False:
            raise HTTPException(401, "Wrong email or password")

        role_user = result.role_id

        email_verification = result.email_verified

        if email_verification is False:
            False

        if role_user is None:
            raise HTTPException(
                404,
                "Oops, Not found!"
            )
        elif role_user == 1:
            return JSONResponse(
                status_code=200,
                content={
                    "role": "user",
                    "access": "permitted"
                }
            )
        elif role_user == 2:
            return JSONResponse(
                status_code=200,
                content={
                    "role": "admin",
                    "access": "permitted"
                }
            )
        else:
            raise HTTPException(
                409,
                "Oops :( , Something went wrong"
            )
    @staticmethod
    async def admin_check(session, email, password):

        query = await session.execute(
            select(
                model.users
            ).where(
                model.users.email == email
            )
        )
        result = query.scalar_one_or_none()

        if result is None:
            raise HTTPException(
                401, "Admin user or password incorrect"
            )

        check_pass = bcrypt.checkpw(
            password.encode("utf-8"),
            result.password.encode("utf-8")
        )

        if check_pass == False:
            raise HTTPException(
                404, "Admin user or password incorrect"
            )

        role = result.role_id

        if role != 2:
            raise HTTPException(
                409,
                "You are not admin"
            )

        elif role == 2:
            return True

    @staticmethod
    async def get_user_by_email(session, email: str):

        query = await session.execute(
            select(model.users).where(model.users.email == email)
        )
        result = query.scalar_one_or_none()

        if result is None:
            raise HTTPException(
                404,
                "Not found user"
            )
        return result

    @staticmethod
    async def update_user_email_verification(user: users, user_data: dict,session: AsyncSession,):
        for k,v in user_data.items():
            setattr(user, k, v)

        await session.commit()
        return {"msg": "success"}

user_regulation = user_service()



def create_safe_url_token(data: dict):

    token = serializer.dumps(data, salt="email-configuration")

    return token

def decode_url_safe_token(token):

    token_data = serializer.loads(token)

    return token_data

    