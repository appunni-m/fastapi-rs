"""Independent input workload for route-dependent response status mutation."""

from fastapi import FastAPI, Response


def create_app() -> FastAPI:
    app = FastAPI()
    records = {"kept": "existing record"}

    @app.put("/catalog/{record_id}")
    def update_record(record_id: str, response: Response) -> str:
        if record_id not in records:
            records[record_id] = "new record"
            response.status_code = 201
        return records[record_id]

    return app
