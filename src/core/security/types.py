from typing import Optional

from uuid import UUID
from pydantic import BaseModel


class UserProtocol(BaseModel):
    id: Optional[UUID]
    is_superuser: bool
