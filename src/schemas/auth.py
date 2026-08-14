from pydantic import BaseModel, EmailStr


class auth_log_in(BaseModel):
    email: EmailStr
    password: str

class emailSchema(BaseModel):
    email: EmailStr