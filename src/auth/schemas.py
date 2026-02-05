from pydantic import BaseModel, SecretStr


class AuthUserSchema(BaseModel):
    email: str
    password: str


class LoginBody(BaseModel):
    email: str
    password: SecretStr
