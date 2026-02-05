from typing import Annotated, Any, TypeVar, Optional
from uuid import UUID

from fastapi import Depends, Request, status, HTTPException

from src.core.exceptions import NotAuthenticated, NotProcessableEntity, PermissionDenied
from src.core.security.dependencies import CurrentUserDep
from src.user.schemas import User


UserT = TypeVar("UserT", bound="User")

class PermissionBase:
    async def __call__(self, request: Request) -> Any:
        """
        Базовый класс. Все наследники должны проверять/возвращать пользователя из request.state
        """
        raise NotImplementedError


class RequireSelfOrSuperuser(PermissionBase):
    param: str = "user_id"

    async def __call__(self, request: Request) -> None:
        user = request.state.user
        if user is None:
            raise NotAuthenticated()
        
        user_id_str = request.path_params.get(self.param)
        if not user_id_str:
            raise RuntimeError("Route must have user_id param")
        
        try:
            target_id = UUID(user_id_str)
        except ValueError:
            raise NotProcessableEntity(detail="Invalid user_id")

        if not (user.id == target_id or user.is_superuser):
            raise PermissionDenied()

class CurrentUser(PermissionBase):
    def __init__(
        self,
        optional: bool = False,
        active: bool = True,
        verified: bool = False,
        superuser: bool = False,
    ):
        self.optional = optional
        self.active = active
        self.verified = verified
        self.superuser = superuser

    async def __call__(self, request: Request) -> Optional[UserT]:
        user: Optional[UserT] = request.state.user

        if self.optional:
            return None
        
        if user is None:
            raise NotAuthenticated()

        if self.active and not user.is_active:
            raise NotAuthenticated(detail="User account is inactive")
        
        if self.verified and not user.is_verified:
            raise PermissionDenied(detail="Email / account not verified")

        if self.superuser and not user.is_superuser:
            raise PermissionDenied(detail="Superuser privileges required")

        return user


require_self_or_superuser = RequireSelfOrSuperuser()
