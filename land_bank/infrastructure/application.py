from typing import Iterable

from fastapi_jsonrpc import API, Entrypoint


def create_app(
		entrypoints: Iterable[Entrypoint],
		**kwargs
) -> API:
	"""Application FastAPI factory
	:param entrypoints: Entrypoints
	:param kwargs: APP settings
	:return: Application variable
	"""
	app: API = API(**kwargs)

	for entrypoint in entrypoints:
		app.bind_entrypoint(entrypoint)

	return app
