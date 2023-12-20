from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, PendingRollbackError
from .session import ASYNC_CONTEXT_SESSION, get_async_session
from typing import Coroutine, Callable, Union

from infrastructure.exception import rpc_exceptions


def transaction(func: Union[Coroutine, Callable]):
	async_session: AsyncSession = get_async_session()
	ASYNC_CONTEXT_SESSION.set(async_session)

	async def wrapper(*args, **kwargs):
		try:
			result = await func(*args, **kwargs)
			await async_session.commit()
			return result
		except (IntegrityError, PendingRollbackError) as e:
			await async_session.rollback()
			raise rpc_exceptions.TransactionError(data=str(e))
		finally:
			await async_session.close()

	return wrapper
