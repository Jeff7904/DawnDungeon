
from datetime import datetime, timedelta
from dawndungeon import config, mongodb
from dawndungeon.api.routers.authentication.schemas import Token, TokenData
from dawndungeon.db.mongodb.entities.session import Session
from dawndungeon.db.mongodb.entities.user import User, UserInDB
from fastapi import Depends, HTTPException, status, APIRouter, Security
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import ValidationError
from typing import Optional, Any, Annotated, List

router: APIRouter = APIRouter()

oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="token")

pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY: str = config.get("SECRET_KEY")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str) -> Optional[UserInDB]:
    user: Optional[UserInDB] = mongodb.get_user(username)
    return user

def insert_user(username: str, password: str) -> UserInDB:
    user: UserInDB = UserInDB(
        username=username,
        hashed_password=hash_password(password)
    )
    mongodb.insert_user(user)
    return user

def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    user: Optional[UserInDB] = get_user(username)
    if not user:
        return insert_user(username, password)
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user

async def get_current_active_user(
    current_user: Annotated[User, Security(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": form_data.scopes},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Security(get_current_active_user)]
):
    return current_user

@router.get("/users/me/sessions/")
async def read_users_me_sessions(
    current_user: Annotated[User, Security(get_current_active_user, scopes=["sessions"])]
):
    sessions: List[Session] = mongodb.get_user_sessions(current_user)
    return JSONResponse(content={"sessions": [session.dict() for session in sessions]})
