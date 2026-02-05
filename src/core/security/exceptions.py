class ErrorCode:
    REFRESH_TOKEN_NOT_VALID = "Refresh token is not valid."
    INVALID_PARAMS = "Invalid UUID."


class AuthError(Exception): ...


class RefreshTokenNotValid(AuthError):
    detail = ErrorCode.REFRESH_TOKEN_NOT_VALID


class InvalidParams(AuthError):
    detail = ErrorCode.INVALID_PARAMS

