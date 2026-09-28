from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, FastAPI


@dataclass(frozen=True)
class AppSettings:
    app_name: str
    admin_email: str
    items_per_user: int


def get_settings() -> AppSettings:
    return AppSettings("Default API", "admin@example.test", 50)


def create_app() -> FastAPI:
    app = FastAPI()

    def override_settings() -> AppSettings:
        return AppSettings("Fixture API", "fixture-admin@example.test", 7)

    app.dependency_overrides[get_settings] = override_settings

    @app.get("/info")
    async def read_info(
        settings: Annotated[AppSettings, Depends(get_settings)],
    ) -> dict[str, object]:
        return {
            "app_name": settings.app_name,
            "admin_email": settings.admin_email,
            "items_per_user": settings.items_per_user,
        }

    return app
