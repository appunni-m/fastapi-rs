"""Independent ASGI stimuli for included routers and router dependencies."""

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException


def create_app() -> FastAPI:
    async def require_query_token(token: str) -> str:
        if token != "jessica":
            raise HTTPException(status_code=400, detail="No Jessica token provided")
        return token

    async def require_header_token(x_token: str = Header()) -> str:
        if x_token != "fake-super-secret-token":
            raise HTTPException(status_code=400, detail="X-Token header invalid")
        return x_token

    app = FastAPI(dependencies=[Depends(require_query_token)])
    users = APIRouter()

    @users.get("/")
    def read_users():
        return [{"username": "Rick"}, {"username": "Morty"}]

    @users.get("/me")
    def read_user_me():
        return {"username": "fakecurrentuser"}

    @users.get("/{username}")
    def read_user(username: str):
        return {"username": username}

    app.include_router(users, prefix="/users")

    items = APIRouter(
        prefix="/items",
        tags=["items"],
        dependencies=[Depends(require_header_token)],
        responses={404: {"description": "Not found"}},
    )
    fake_items = {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}

    @items.get("/")
    def read_items():
        return fake_items

    @items.get("/{item_id}")
    def read_item(item_id: str):
        if item_id not in fake_items:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"name": fake_items[item_id]["name"], "item_id": item_id}

    @items.put(
        "/{item_id}",
        tags=["custom"],
        responses={403: {"description": "Operation forbidden"}},
    )
    def update_item(item_id: str):
        if item_id != "plumbus":
            raise HTTPException(
                status_code=403, detail="You can only update the item: plumbus"
            )
        return {"item_id": item_id, "name": "The great Plumbus"}

    app.include_router(items)

    admin = APIRouter()

    @admin.post("/")
    def update_admin():
        return {"message": "Admin getting schwifty"}

    app.include_router(
        admin,
        prefix="/admin",
        tags=["admin"],
        dependencies=[Depends(require_header_token)],
        responses={418: {"description": "I'm a teapot"}},
    )
    return app
