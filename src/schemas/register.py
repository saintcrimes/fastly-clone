from pydantic import BaseModel, EmailStr, Field


class Register(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    company_name: str
    job_title: str
    password: str


class Admin_OK(BaseModel):
    email: EmailStr
    password: str

class PasswordChange(BaseModel):
    password: str = Field(min_length=8, max_length=20)