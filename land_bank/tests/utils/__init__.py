from typing import Any

from fastapi_jsonrpc import JsonRpcRequest


def json_rpc_body(method: str, params: Any) -> dict:
    return JsonRpcRequest(id='0', method=method, params=params).model_dump()
