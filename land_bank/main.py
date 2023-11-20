from fastapi_jsonrpc import API
from auth import auth_application

app = API()

app.bind_entrypoint(auth_application)
