
from dawndungeon import config
from dawndungeon.api.routers import authentication_router, game_router
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(debug=config.get("DEBUG"))
app.include_router(authentication_router)
app.include_router(game_router)
app.add_middleware(SessionMiddleware, secret_key=config.get("SECRET_KEY"))

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
