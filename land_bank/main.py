from fastapi.middleware.cors import CORSMiddleware
from fastapi_jsonrpc import API

from infrastructure.settings import AppSettings
from infrastructure import application
from endpoint import rest, rpc

RPC_ENTRYPOINTS = (
	rpc.auth.router,
	rpc.employee.router,
	rpc.area_comment.router,
	rpc.land_area.router,
	rpc.scheduler.router,
)

REST_ENTRYPOINT = (
	rest.employee.router,
)

app: API = application.create_app(
	rpc_entrypoints=RPC_ENTRYPOINTS,
	rest_entrypoints=REST_ENTRYPOINT)

app.add_middleware(
	CORSMiddleware,
	allow_origins=[AppSettings.FRONTEND_HOST],
	allow_credentials=True,
	allow_methods=['POST'],
	allow_headers=['*']
)
