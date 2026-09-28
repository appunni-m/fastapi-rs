"""Independent workload for extra-model request and response workflows."""

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr


class ItemBase(BaseModel):
    description: str
    type: str


class CarItem(ItemBase):
    type: str = "car"


class PlaneItem(ItemBase):
    type: str = "plane"
    size: int


class Item(BaseModel):
    name: str
    description: str


_UNION_ITEMS = {
    "coupe": {"description": "A quiet electric coupe", "type": "car"},
    "jet": {
        "description": "A high altitude passenger jet",
        "type": "plane",
        "size": 8,
    },
}

_CATALOG_ITEMS = [
    {"name": "Cedar", "description": "Lightweight field notebook"},
    {"name": "Harbor", "description": "Weatherproof travel journal"},
]


def _create_user_models(style: str) -> tuple[type[BaseModel], type[BaseModel], type[BaseModel]]:
    if style == "flat":

        class UserIn(BaseModel):
            username: str
            password: str
            email: EmailStr
            full_name: str | None = None

        class UserOut(BaseModel):
            username: str
            email: EmailStr
            full_name: str | None = None

        class UserInDB(BaseModel):
            username: str
            hashed_password: str
            email: EmailStr
            full_name: str | None = None

    elif style == "inherited":

        class UserBase(BaseModel):
            username: str
            email: EmailStr
            full_name: str | None = None

        class UserIn(UserBase):
            password: str

        class UserOut(UserBase):
            pass

        class UserInDB(UserBase):
            hashed_password: str

    else:
        raise ValueError(f"unsupported user model style: {style}")

    return UserIn, UserOut, UserInDB


def _add_user_route(app: FastAPI, style: str) -> None:
    user_in, user_out, user_in_db = _create_user_models(style)

    def store_user(user: BaseModel) -> BaseModel:
        saved = user.model_dump()
        raw_password = saved.pop("password")
        saved["hashed_password"] = f"stored:{raw_password}"
        return user_in_db(**saved)

    @app.post("/user/", response_model=user_out)
    async def create_user(user_in: user_in) -> BaseModel:
        return store_user(user_in)


def _add_union_route(app: FastAPI) -> None:
    @app.get("/items/{item_id}", response_model=PlaneItem | CarItem)
    async def read_item(item_id: str) -> dict[str, str | int]:
        return _UNION_ITEMS[item_id]


def _add_list_route(app: FastAPI) -> None:
    @app.get("/items/", response_model=list[Item])
    async def read_items() -> list[dict[str, str]]:
        return _CATALOG_ITEMS


def _add_map_route(app: FastAPI) -> None:
    @app.get("/keyword-weights/", response_model=dict[str, float])
    async def read_keyword_weights() -> dict[str, float]:
        return {"alpha": 1.25, "beta": 2.75}


def create_app(factory_input: dict[str, str], _event_trace: list[str]) -> FastAPI:
    app = FastAPI()
    workflow = factory_input["workflow"]
    if workflow == "user":
        _add_user_route(app, factory_input["user_model_style"])
    elif workflow == "union":
        _add_union_route(app)
    elif workflow == "list":
        _add_list_route(app)
    elif workflow == "map":
        _add_map_route(app)
    else:
        raise ValueError(f"unsupported extra-model workflow: {workflow}")
    return app
