from fastapi_jsonrpc import BaseError


# Codes since 32001

class UniqueEmailError(BaseError):
	"""Ошибка вызывается, если при регистрации указан emailб который уже есть
	в БД (IntegrityError)"""

	CODE = -32001
	MESSAGE = 'User with current email already exists'


class LoginError(BaseError):
	"""Ошибка при попытке аутетифицировать пользователя"""

	CODE = -32002
	MESSAGE = 'Incorrect login data'


class AuthenticationError(BaseError):
	"""
	Ошибка при аутентификации пользователя
	HTTP Аналог - 401 Unauthorized
	"""

	CODE = -32003
	MESSAGE = 'Authentication Error'


class ValidationFileError(BaseError):
	"""Ошибка при валидации файла"""

	CODE = -32004
	MESSAGE = 'File signature is incorrect'


class TransactionError(BaseError):
	"""Ошибка при транзакции"""
	CODE = -32005
	MESSAGE = 'Transaction Error'


class AuthorizationError(BaseError):
	"""
	Ошибка при проверке прав пользователя
	HTTP Аналог - 401 Unauthorized
	"""
	CODE = -32006
	MESSAGE = 'Authorization Error'


class ObjectNotFoundError(BaseError):
	"""
	Ошибка если сущность не существует
	HTTP Аналог - 404 Not found
	"""
	CODE = -32007
	MESSAGE = 'Object does not exist'


class TransactionForbiddenError(BaseError):
	"""
	Ошибка, если транзакция не разрешена пользователю
	HTTP Аналог - 403 Forbidden
	"""
	CODE = -32008
	MESSAGE = 'Transaction is not available'
