"""Independent FastAPI request inputs for the settings documentation review."""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, FastAPI


@dataclass(frozen=True)
class AppSettings:
    app_name: str
    admin_email: str
    items_per_user: int


_SETTINGS = AppSettings("Fixture API", "admin@example.test", 7)


def get_settings() -> AppSettings:
    return _SETTINGS


def create_app() -> FastAPI:
    app = FastAPI()

    def get_settings_override() -> AppSettings:
        return AppSettings("Test API", "test-admin@example.test", 11)

    app.dependency_overrides[get_settings] = get_settings_override

    @app.get("/global-info")
    async def read_info() -> dict[str, object]:
        return {
            "app_name": _SETTINGS.app_name,
            "admin_email": _SETTINGS.admin_email,
            "items_per_user": _SETTINGS.items_per_user,
        }

    @app.get("/info")
    async def read_dependency_info(
        settings: Annotated[AppSettings, Depends(get_settings)],
    ) -> dict[str, object]:
        return {
            "app_name": settings.app_name,
            "admin_email": settings.admin_email,
            "items_per_user": settings.items_per_user,
        }

    return app
