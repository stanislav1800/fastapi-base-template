from pwdlib import PasswordHash


class PasswordHasher:
    def __init__(self):
        self._hasher = PasswordHash.recommended()

    def hash(self, password: str) -> str:
        """Хэширует пароль, используя текущий хэшер"""
        return self._hasher.hash(password)

    def verify(self, plain: str, hashed: str) -> bool:
        """Проверяет, соответствует ли пароль заданному хэшу"""
        return self._hasher.verify(plain, hashed)
