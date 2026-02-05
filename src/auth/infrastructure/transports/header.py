from fastapi import Request, Response

from .base import AuthTransportBase


class HeaderTransport(AuthTransportBase):
    def __init__(
        self,
        header_name: str = "Authorization",
        token_type_prefix: str | None = "Bearer",
    ) -> None:
        self.header_name = header_name
        self.token_type_prefix = token_type_prefix

    def set_token(self, response: Response, token: str) -> None:
        if self.token_type_prefix:
            token_value = f"{self.token_type_prefix} {token}"
        else:
            token_value = token
        response.headers[self.header_name] = token_value

    def delete_token(self, response: Response) -> None:
        response.headers[self.header_name] = ""

    def get_token(self, request: Request) -> str | None:
        header = request.headers.get(self.header_name, None)
        if header:
            try:
                return header.split(" ")[1]
            except IndexError:
                return header
