import os

from typing import Optional

import requests


Token = str
ResponseError = tuple[str, int]


def login(request: requests.Request) -> tuple[Token | None, Optional[ResponseError]]:
    """Forward login request to auth service"""
    auth = request.authorization
    if not auth:
        return None, ("Missing credentials", 401)

    basicAuth = (auth.username, auth.password)
    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login", auth=basicAuth
    )
    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)


def validate_token(request: requests.Request) -> tuple[str, tuple[str, int]]:
    """
    Forward token to auth service for validatio and return the token's
    information
    """
    if not "Authorization" in request.headers:
        return None, ("missing credentials", 401)

    token = request.headers["Authorization"]

    if not token:
        return None, ("Missing credentials", 401)

    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate",
        headers={"Authorization": token},
    )

    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)
