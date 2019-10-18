from fastapi import Depends, FastAPI

app = FastAPI()

"""
# Dependency injection: a function that abstracts logic and can be provided to
# other functions as dependency.

Whenever a new request arrives to a function that includes a dependency, fastAPI 
runs the dependency function with the corresponding parameters, and it then
assign the result of this dependency as path parameters to the view func.

"""
async def common_parameters(q: str = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}


@app.get("/items/")
async def read_items(commons: dict = Depends(common_parameters)):
    """ Declare the dependency in the dependant """
    return commons


@app.get("/users/")
async def read_users(commons: dict = Depends(common_parameters)):
    return commons

"""
Dependencies that don't relate to the path parameters, or that don't return anything
but still need to be ran before the request, can be added as a list to the decorator
"""

async def verify_token(x_token: str = Header(...)):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key(x_key: str = Header(...)):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key


@app.get("/items/", dependencies=[Depends(verify_token), Depends(verify_key)])
async def read_items():
    return [{"item": "Foo"}, {"item": "Bar"}]

"""
Deependencies with `yield`:
if a dependency has some code that needs to run before the response is sent, and some that
needs to run after, can use the yield keyword. Everything that is before (and up to) the yield 
keyword will run before sending the response, and anything that's after will run after
"""
async def get_db():
    db = DBSession()
    try:
        # This yielded value is injected into path operations and other deps.
        yield db
    finally:
        db.close()
