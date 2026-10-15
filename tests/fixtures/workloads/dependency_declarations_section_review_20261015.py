"""Independent workload for decorator dependencies with discarded return values."""

from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException


def create_app(factory_input: dict[str, str], event_trace: list[str]) -> FastAPI:
    del factory_input
    app = FastAPI()

    async def require_stockroom(x_store_access: Annotated[str, Header()]):
        if x_store_access != "allow-stockroom":
            raise HTTPException(status_code=403, detail="Stockroom access rejected")
        event_trace.append("stockroom-access")

    async def reserve_parcel(x_parcel_key: Annotated[str, Header()]):
        if x_parcel_key != "parcel-41":
            raise HTTPException(status_code=403, detail="Parcel key rejected")
        event_trace.append("parcel-reserved")
        return "reserved:" + x_parcel_key

    @app.get("/stock", dependencies=[Depends(require_stockroom), Depends(reserve_parcel)])
    async def read_stock():
        return {"stock": "ready"}

    @app.get("/trace")
    async def read_trace():
        return {"events": list(event_trace)}

    return app
