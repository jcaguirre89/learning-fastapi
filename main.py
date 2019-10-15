from enum import Enum

from fastapi import FastAPI


class ModelName(str, Enum):
    """ inherit from str so the docs know what to expect """

    alexnet = "AlexNet"
    lightgbm = "Light GBM"


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}


@app.get("/model/{model_name}")
async def get_model(model_name: ModelName):
    """
    Two different ways to access a restricted number of options.
    First is accessing the Enum's attributes and the other is
    directly with the expected value
    """
    if model_name == ModelName.alexnet:
        return {"model name": model_name, "msg": "DL"}
    if model_name.value == "Light GBM":
        return {"model name": model_name, "msg": "LGBM"}
    # This line won't run
    # it will return error if the given parameter isn't in the Enum
    return {"msg": "what"}


@app.get("/files/{file_path:path}")
async def read_user_me(file_path: str):
    """ Declaring a file path """
    return {"file_path": file_path}


fake_db_items = [{"name": "Juan"}, {"name": "Cristobal"}]


@app.get("/names/")
async def get_names(skip: int = 0, limit: int = 10):
    """ arguments given to the view but not part of the path
    parameters are interpreted as query strings
    http://localhost:8000/names/?skip=1
    """
    return fake_db_items[skip : skip + limit]


# Request body (data) with Pydantic models
from pydantic import BaseModel, Schema


class Item(BaseModel):
    """
    a model
    """

    name: str  # required
    description: str = None  # optional
    price: float = Schema(..., gt=0, description="Some desc", title="My Price")
    tax: float = None


@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_w_tax = item.price + item.tax
        item_dict.update({"price_w_tax": price_w_tax})
    return item_dict


# Additional data validation for query params w Query
from fastapi import Query


@app.get("/validated-items/")
async def read_validate_items(
    q: str = Query(
        None,  # same as q: str = None
        title="Query string",
        description="Some description to show in the docs",
        max_length=50,
        min_length=3,
    )
):
    """
    use the Query class as the default instead of a python base type.
    http://localhost:8000/validated-items/?q=some-query
    """
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# Validate path parameters with Path
from fastapi import Path


@app.get("/cats/{cat_id}")
async def read_cats(
    *,
    cat_id: int = Path(
        ...,  # paths are always required so this could be ..., None, etc.
        title="The ID of the cat, that must be greater than 10",
        ge=10,
    ),
    q: str = None,
):
    results = {"cat_id": cat_id}
    if q:
        results.update({"q": q})
    return results


@app.put("/items/{item_id}")
async def update_item(
    *,
    item_id: int = Path(..., title="The ID of the item to get", ge=0, le=1000),
    q: str = None,
    item: Item = None,
):
    """
    Optional body params by setting default to None
    """
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if item:
        results.update({"item": item})
    return results

# Nested models
from typing import Set
from pydantic import UrlStr

class Image(BaseModel):
    url: UrlStr
    name: str

class Product(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None
    tags: Set[str] = []
    image: Image = None

@app.post('/products/{product_id}')
async def create_product(*, product_id: int, product: Product):
    """
    Expected body:
        {
          "name": "string",
          "price": 0,
          "description": "string",
          "tax": 0,
          "tags": [
            "string"
          ],
          "image": {
            "url": "string",
            "name": "string"
          }
        }
    """
    results = {'product_id': product_id, 'product': product}
    return results


# Response models
from pydantic.types import EmailStr
class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str = None


class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: str = None


@app.post("/user/", response_model=UserOut)
async def create_user(*, user: UserIn):
    """ receive a UserIn body and return a UserOut """
    return user
