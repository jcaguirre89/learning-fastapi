from typing import Optional

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

# This returns a callable that can be used as dependency
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

class User(BaseModel):
    username: str
    email: Optional[str] = None 
    full_name: Optional[str] = None 
    disabled: Optional[bool] = None 


def decode_token(token):
    """ dummy func that would read the JWT """
    return User(username=token+"fakedecoded", email='some@email.com', full_name='Some Name')


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    oauth2 dependency returns a token as a str when the user 
    authenticates by going to /token and providing a valid
    username + password
    """
    user = decode_token(token)
    return user


app = FastAPI()


@app.get("/items/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}

@app.get('/users/me')
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
