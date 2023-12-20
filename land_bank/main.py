from fastapi.middleware.cors import CORSMiddleware
from fastapi_jsonrpc import API

from infrastructure.settings import AppSettings
from infrastructure import application
from endpoint.rpc import *

ENTRYPOINTS = (
	employee.router,
	area_comment.router,
	land_area.router,
	scheduler.router,
)

app: API = application.create_app(
	entrypoints=ENTRYPOINTS,
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=[AppSettings.FRONTEND_HOST],
	allow_credentials=True,
	allow_methods=['POST'],
	allow_headers=['*']
)
