from fastapi_jsonrpc import BaseError


# Codes since 32001

class UniqueEmailError(BaseError):
    """Ошибка вызывается, если при регистрации указан emailб который уже есть в БД (IntegrityError)"""

    CODE = -32001
    MESSAGE = 'User with current email already exists'


class LoginError(BaseError):
    """Ошибка при попытке аутетифицировать пользователя"""

    CODE = -32002
    MESSAGE = 'Incorrect login data'


class AuthenticationError(BaseError):
    """Ошибка при аутентификации пользователя"""

    CODE = -32003
    MESSAGE = 'Authorization Error'


class ValidationFileError(BaseError):
    """Ошибка при валидации файла"""

    CODE = -32004
    MESSAGE = 'File signature is incorrect'
