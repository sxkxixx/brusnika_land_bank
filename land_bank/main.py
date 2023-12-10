from fastapi_jsonrpc import API
from auth import auth_application
from fastapi.middleware.cors import CORSMiddleware
from core import Config
from bank.endpoints import areas_endpoint

app = API()

app.bind_entrypoint(auth_application)
app.bind_entrypoint(areas_endpoint)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[Config.FRONTEND_HOST],
    allow_credentials=True,
    allow_methods=['POST'],
    allow_headers=['*']
)
