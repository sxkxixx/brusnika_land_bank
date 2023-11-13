from fastapi_jsonrpc import BaseError


# Codes since 32001

class UniqueEmailError(BaseError):
    """Ошибка вызывается при попытке регистрации пользователя."""

    CODE = -32001
    MESSAGE = 'User with current email already exists'


class LoginError(BaseError):
    """Ошибка при аутентификации"""

    CODE = -32002
    MESSAGE = 'Incorrect login data'


class AuthorizationError(BaseError):
    """Ошибка при авторизации пользователя"""

    CODE = -32003
    MESSAGE = 'Authorization Error'
