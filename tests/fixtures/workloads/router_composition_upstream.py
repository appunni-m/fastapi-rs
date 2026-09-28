"""Independent ASGI stimuli for included routers and router dependencies."""

from fastapi import APIRouter, Depends, FastAPI


def create_app() -> FastAPI:
    app = FastAPI()
    users = APIRouter()

    def require_token(token: str) -> str:
        return token

    @users.get("/")
    def read_users(token: str = Depends(require_token)):
        return [{"username": "Rick"}, {"username": "Morty"}]

    @users.get("/me")
    def read_user_me(token: str = Depends(require_token)):
        return {"username": "fakecurrentuser"}

    @users.get("/{username}")
    def read_user(username: str, token: str = Depends(require_token)):
        return {"username": username}

    app.include_router(users, prefix="/users")
    return app
