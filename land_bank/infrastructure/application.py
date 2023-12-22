from typing import Iterable

from fastapi_jsonrpc import API, Entrypoint
from fastapi import APIRouter


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

	return app
