from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    username: str
    email: str 

class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    username: str or None = None
