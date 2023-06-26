
from pydantic import BaseModel
from typing import Optional, List

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []

class Token(BaseModel):
    access_token: str
    token_type: str
