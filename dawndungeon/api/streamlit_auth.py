from dawndungeon import config
from numpy import void
import streamlit as st
import asyncio
from httpx_oauth.clients.google import GoogleOAuth2
from typing import Any, Tuple

CLIENT_ID = config.get("GOOGLE_CLIENT_ID")
CLIENT_SECRET = config.get("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:8502"


async def get_authorization_url(client: GoogleOAuth2, redirect_uri: str):
    authorization_url = await client.get_authorization_url(
        redirect_uri, scope=["profile", "email"]
    )
    return authorization_url


async def get_access_token(client: GoogleOAuth2, redirect_uri: str, code: str):
    token = await client.get_access_token(code, redirect_uri)
    return token


async def get_email(client: GoogleOAuth2, token: str):
    user_id, user_email = await client.get_id_email(token)
    return user_id, user_email


def get_auth_url():
    client: GoogleOAuth2 = GoogleOAuth2(CLIENT_ID, CLIENT_SECRET)
    authorization_url = asyncio.run(get_authorization_url(client, REDIRECT_URI))
    return authorization_url


def get_user_details() -> Tuple[Any, Any]:
    client: GoogleOAuth2 = GoogleOAuth2(CLIENT_ID, CLIENT_SECRET)
    # get the code from the url
    code = st.experimental_get_query_params()["code"]
    token = asyncio.run(get_access_token(client, REDIRECT_URI, code))
    user_id, user_email = asyncio.run(get_email(client, token["access_token"]))
    return (user_id, user_email)
