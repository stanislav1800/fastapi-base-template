from fastapi import APIRouter, Depends, Request, status
from uuid import UUID

from src.core.security.permissions import CurrentUser, require_self_or_superuser
from src.user.dependencies import PasswordHasherDep, UserUOWDep
from src.user.schemas import UserCreateBody, UserResponse, UserUpdateBody
from src.user.service import delete_user, get_user_profile, register_user, update_user

router = APIRouter()

get_current_active_user = CurrentUser(active=True)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_active_user)):
    """
    Retrieve the profile of the currently authenticated user.
    """
    return current_user


@router.post("", response_model=UserResponse)
async def register(user_data: UserCreateBody, pwd_hasher: PasswordHasherDep, uow: UserUOWDep):
    """
    Register a new user.
    """
    return await register_user(user_data, pwd_hasher, uow)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    # dependencies=[Depends(get_current_active_user)]
)
async def get_profile(user_id: UUID, uow: UserUOWDep):
    """
    Get user profile by ID.
    """
    return await get_user_profile(user_id, uow)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_self_or_superuser)],
)
async def update(user_id: UUID, user_data: UserUpdateBody, uow: UserUOWDep):
    """
    Update user data.
    """
    return await update_user(user_id, user_data, uow)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_self_or_superuser)],
)
async def delete(user_id: UUID, uow: UserUOWDep):
    """
    Delete user by ID.
    """
    await delete_user(user_id, uow)
