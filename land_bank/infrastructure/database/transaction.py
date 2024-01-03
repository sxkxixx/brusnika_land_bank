from typing import Coroutine, Callable, Union
from functools import wraps
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.exception import rpc_exceptions
from .session import ASYNC_CONTEXT_SESSION, get_async_session
from sqlalchemy.exc import IntegrityError, PendingRollbackError

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s %(levelname)s: %(message)s"
)


def in_transaction(func: Union[Coroutine, Callable]):
	# TODO: Переписать работу с базой, используя декоратор in_transaction
	@wraps(func)
	async def wrapper(*args, **kwargs):
		async_session: AsyncSession = get_async_session()
		ASYNC_CONTEXT_SESSION.set(async_session)

		logging.info(
			f'Transaction session is_active='
			f'{ASYNC_CONTEXT_SESSION.get().is_active}, '
			f'Function Name: {func.__name__}'
		)
		try:
			result = await func(*args, **kwargs)
			await async_session.commit()
			logging.info(f'Transaction success: {func.__name__}')
			return result
		except (IntegrityError, PendingRollbackError) as e:
			logging.error(
				f'Transaction error: error type = {type(e)}, '
				f'errors msg = {str(e)}')
			await async_session.rollback()
			raise rpc_exceptions.TransactionError(data=str(e))
		finally:
			await async_session.close()
			logging.info(f'Session closed: {func.__name__}')
	return wrapper
