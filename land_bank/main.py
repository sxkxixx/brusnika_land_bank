from fastapi.middleware.cors import CORSMiddleware
from fastapi_jsonrpc import API

from endpoint import rest, rpc
from infrastructure import application
from infrastructure.settings import AppSettings

RPC_ENTRYPOINTS = (
    rpc.auth.router,
    rpc.employee.router,
    rpc.area_comment.router,
    rpc.land_area.router,
    rpc.scheduler.router,
    rpc.juristic_data.router,
    rpc.extra_data.router
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
