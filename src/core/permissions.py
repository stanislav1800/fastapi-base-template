from functools import wraps
from uuid import UUID

from fastapi import HTTPException, status

from src.core.exceptions import PermissionDenied
from src.user.models import User


def permission_policy(check_func):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User, target_id: UUID = None, **kwargs):
            await check_func(current_user, target_id)
            return await func(*args, current_user=current_user, target_id=target_id, **kwargs)
        return wrapper
    return decorator


async def can_manage_user(current_user: User, target_id: UUID):
    if current_user.is_superuser:
        return
    if current_user.id != target_id:
        raise PermissionDenied()

