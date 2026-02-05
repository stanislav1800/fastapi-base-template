from typing import Annotated

from fastapi import Depends, Request

from src.core.exceptions import NotAuthenticated
from src.user.schemas import User


def get_current_user(request: Request) -> User:
    if not hasattr(request.state, "user"):
        raise NotAuthenticated()
    return request.state.user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
