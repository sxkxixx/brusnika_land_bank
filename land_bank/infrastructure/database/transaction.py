import logging
from functools import wraps
from typing import Any, Callable

from fastapi_jsonrpc import BaseError
from sqlalchemy.exc import IntegrityError, PendingRollbackError
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.exception import rpc_exceptions
from .session import ASYNC_CONTEXT_SESSION, get_async_session

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s"
)


def in_transaction(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        async_session: AsyncSession = get_async_session()
        ASYNC_CONTEXT_SESSION.set(async_session)

        logging.info(
            f'Transaction session is_active='
            f'{ASYNC_CONTEXT_SESSION.get().is_active}, '
            f'Function Name: {func.__name__}'
        )
        try:
            result: Any = await func(*args, **kwargs)
            await async_session.commit()
            logging.info(f'Transaction success: {func.__name__}')
            return result
        except BaseError as rpc_error:
            logging.error(f'Transaction error: {type(BaseError)}')
            await async_session.rollback()
            raise rpc_error
        except (IntegrityError, PendingRollbackError) as e:
            logging.error(
                f'Transaction error: error type = {type(e)}')
            await async_session.rollback()
            print(e.args)
            raise rpc_exceptions.TransactionError(
                data='Error while transaction executing')
        finally:
            await async_session.close()
            logging.info(f'Session closed: {func.__name__}')

    return wrapper
