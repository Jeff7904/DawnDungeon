
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse, JSONResponse, HTMLResponse, RedirectResponse
from starlette.routing import Route
from starlette.staticfiles import StaticFiles
from starlette.requests import Request
from starlette.templating import Jinja2Templates, _TemplateResponse
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
import os
import json
import requests
from authlib.integrations.starlette_client import OAuth, OAuthError
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# OAuth settings
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID') or None
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET') or None
if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
    raise BaseException('Missing env variables')

# Set up oauth
config_data = {'GOOGLE_CLIENT_ID': GOOGLE_CLIENT_ID, 'GOOGLE_CLIENT_SECRET': GOOGLE_CLIENT_SECRET}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account', # force to select account
    }
)

app = Starlette(
    debug=True,
)

app.mount("/dawndungeon-frontend/static", StaticFiles(directory="dawndungeon-frontend/static"), name="static")

SECRET_KEY = os.environ.get('SECRET_KEY') or None
if (SECRET_KEY is None):
    raise 'Missing SECRET_KEY'
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, max_age=None)

templates = Jinja2Templates(directory="dawndungeon-frontend/templates")

@app.route('/')
async def homepage(request: Request):
    user = request.session.get('user')
    access_token = request.session.get('access_token')
    if user:
        context = {"request": request, "access_token": access_token}
        return RedirectResponse(url='http://localhost:8502')
        return templates.TemplateResponse("index.html", context)
    # return RedirectResponse(url='/login')

@app.route('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')  # This creates the url for the /auth endpoint
    return await oauth.google.authorize_redirect(request, str(redirect_uri))

@app.route('/auth')
async def auth(request: Request):
    try:
        access_token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        return RedirectResponse(url='/')
    user_data = access_token.get('userinfo')
    request.session['user'] = dict(user_data)
    token = requests.post("http://localhost:8080/token", data={"username": user_data['name'], "password": user_data['name']}).json()
    request.session['access_token'] = token['access_token'] # Different access_token from backend
    return RedirectResponse(url='/')

@app.route('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')