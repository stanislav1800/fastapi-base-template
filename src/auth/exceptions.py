from src.core.exceptions import BadRequest, NotAuthenticated


class ErrorCode:
    INVALID_CREDENTIALS = "Invalid credentials."
    REFRESH_TOKEN_NOT_VALID = "Refresh token is not valid."
    ACCESS_TOKEN_NOT_VALID = "Access token is not valid."


class InvalidCredentials(NotAuthenticated):
    detail = ErrorCode.INVALID_CREDENTIALS


class RefreshTokenNotValid(NotAuthenticated):
    detail = ErrorCode.REFRESH_TOKEN_NOT_VALID


class AccessTokenNotValid(NotAuthenticated):
    detail = ErrorCode.ACCESS_TOKEN_NOT_VALID
