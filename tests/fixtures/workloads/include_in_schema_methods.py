"""Observe excluded direct HTTP routes still dispatch and stay out of OpenAPI."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/visible")
    def visible():
        return {"method": "GET"}

    @app.get("/hidden-get", include_in_schema=False)
    def hidden_get():
        return {"method": "GET"}

    @app.post("/hidden-post", include_in_schema=False)
    def hidden_post():
        return {"method": "POST"}

    @app.put("/hidden-put", include_in_schema=False)
    def hidden_put():
        return {"method": "PUT"}

    @app.delete("/hidden-delete", include_in_schema=False)
    def hidden_delete():
        return {"method": "DELETE"}

    @app.patch("/hidden-patch", include_in_schema=False)
    def hidden_patch():
        return {"method": "PATCH"}

    @app.head("/hidden-head", include_in_schema=False)
    def hidden_head():
        return {"method": "HEAD"}

    @app.options("/hidden-options", include_in_schema=False)
    def hidden_options():
        return {"method": "OPTIONS"}

    @app.trace("/hidden-trace", include_in_schema=False)
    def hidden_trace():
        return {"method": "TRACE"}

    return app
