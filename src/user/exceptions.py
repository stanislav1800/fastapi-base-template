from src.core.exceptions import AlreadyExists, NotFound, PermissionDenied


class UserAlreadyExists(AlreadyExists):
    detail = "User with this data already exists"


class UserNotFound(NotFound):
    detail = "User with this data not found"


class UserPermission(PermissionDenied):
    detail = "Permission denied"
