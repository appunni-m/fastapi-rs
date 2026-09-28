"""Pydantic field serializer observed through FastAPI response-model output."""

from datetime import datetime, timezone

from fastapi import FastAPI
from pydantic import BaseModel, field_serializer


def create_app() -> FastAPI:
    class ModelWithDatetimeField(BaseModel):
        dt_field: datetime

        @field_serializer("dt_field")
        def serialize_datetime(self, dt_field: datetime) -> str:
            return dt_field.replace(microsecond=0, tzinfo=timezone.utc).isoformat()

    app = FastAPI()
    model = ModelWithDatetimeField(dt_field=datetime(2019, 1, 1, 8))

    @app.get("/model", response_model=ModelWithDatetimeField)
    def get_model() -> ModelWithDatetimeField:
        return model

    return app
