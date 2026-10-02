"""Input workload for base64 validation and serialization of bytes fields."""

from fastapi import FastAPI
from pydantic import BaseModel


class DataInput(BaseModel):
    description: str
    data: bytes

    model_config = {"val_json_bytes": "base64"}


class DataOutput(BaseModel):
    description: str
    data: bytes

    model_config = {"ser_json_bytes": "base64"}


class DataInputOutput(BaseModel):
    description: str
    data: bytes

    model_config = {
        "val_json_bytes": "base64",
        "ser_json_bytes": "base64",
    }


def create_app() -> FastAPI:
    app = FastAPI()

    @app.post("/data")
    def decode_data(body: DataInput) -> dict[str, str]:
        return {"description": body.description, "content": body.data.decode("utf-8")}

    @app.get("/data")
    def encode_data() -> DataOutput:
        return DataOutput(description="independent output", data=b"independent-output")

    @app.post("/data-in-out")
    def roundtrip_data(body: DataInputOutput) -> DataInputOutput:
        return body

    return app
