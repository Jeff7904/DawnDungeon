
from starlette.requests import Request

def get_session(request: Request) -> dict:
    return request.session
