from typing import Iterable, List

from fastapi import APIRouter
from fastapi_jsonrpc import API, Entrypoint
from sqlalchemy.exc import IntegrityError, PendingRollbackError
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.session import ASYNC_CONTEXT_SESSION
from infrastructure.database.transaction import in_transaction
from storage.limit import LimitRepository
from storage.permitted_use import PermittedUseRepository

__LIMITS: List[str] = [
    'Ипотека', 'Арест', 'Запрет на совершение регистрационных действий',
    'Рента', 'Сервитут', 'Аренда', 'Доверительное управление',
    'Право на безвозмездное пользование'
]

__PERMITTED_USES: List[str] = [
    'Cельскохозяйственное использование',
    'Жилая застройка',
    'Общественное использование объектов капитального строительства',
    'Предпринимательство', 'Отдых',
    'Производственная деятельность', 'Транспорт',
    'Обеспечение обороны и безопасности',
    'Деятельность по особой охране и изучению природы',
    'Использование лесов', 'Водные объекты',
    'Земельные участки общего пользования',
    'Земельные участки общего назначения'
]


async def create_limits(session: AsyncSession) -> None:
    repo = LimitRepository()
    try:
        for limit in __LIMITS:
            await repo.create_limit(session, name=limit)
    except (IntegrityError, PendingRollbackError):
        await session.rollback()


async def create_permitted_uses(session: AsyncSession) -> None:
    repo = PermittedUseRepository()
    try:
        for use in __PERMITTED_USES:
            await repo.create_permitted_use(session, name=use)
    except (IntegrityError, PendingRollbackError):
        await session.rollback()


@in_transaction
async def init_database_variables() -> None:
    session: AsyncSession = ASYNC_CONTEXT_SESSION.get()
    await create_limits(session)
    await create_permitted_uses(session)


def create_app(
        rpc_entrypoints: Iterable[Entrypoint],
        rest_entrypoints: Iterable[APIRouter],
        **kwargs
) -> API:
    """Application FastAPI factory
    :param rpc_entrypoints: REST-API роутеры
    :param rest_entrypoints: JSON-RPC роутеры
    :param kwargs: APP settings
    :return: Application variable
    """
    app: API = API(**kwargs)

    for entrypoint in rpc_entrypoints:
        app.bind_entrypoint(entrypoint)

    for api_router in rest_entrypoints:
        app.include_router(api_router)

    # asyncio.create_task(init_database_variables())

    return app
