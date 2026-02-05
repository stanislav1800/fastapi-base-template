from fastapi import APIRouter, Body, Request

from src.auth.dependencies import PasswordHasherDep, TokenAuthDep
from src.auth.schemas import LoginBody
from src.auth.service import authenticate
from src.user.dependencies import UserUOWDep

router = APIRouter()


@router.post("/login")
async def token(
    auth: TokenAuthDep,
    pwd_hasher: PasswordHasherDep,
    uow: UserUOWDep,
    form_data: LoginBody = Body(),
):
    await authenticate(form_data.email, form_data.password, pwd_hasher, uow, auth)
    return {"detail": "Tokens set"}


@router.post("/refresh")
async def token_refresh(auth: TokenAuthDep):
    refreshed = await auth.refresh_access_token()
    return {"detail": "Token refreshed"}


@router.post("/logout")
async def logout(auth: TokenAuthDep, request: Request):
    await auth.unset_tokens()
    request.state.auth_tokens_cleared = True
    return {"detail": "Tokens deleted"}
