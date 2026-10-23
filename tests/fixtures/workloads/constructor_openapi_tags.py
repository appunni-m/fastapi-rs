"""Independent ASGI inputs for FastAPI's constructor-level OpenAPI tags."""

from typing import Any

from fastapi import FastAPI


def create_app(factory_input: dict[str, Any], _event_trace: list[str]) -> FastAPI:
    if "tags" in factory_input:
        tags = factory_input["tags"]
        app = FastAPI(openapi_tags=tags)
    else:
        tags = None
        app = FastAPI()
    if "append_tag" in factory_input:
        tags.append(factory_input["append_tag"])
    if "delete_openapi_tags" in factory_input:
        del app.openapi_tags
    if "replacement_tags" in factory_input:
        app.openapi_tags = factory_input["replacement_tags"]

    @app.get("/users/", tags=["users"])
    async def get_users():
        return [{"name": "Harry"}, {"name": "Ron"}]

    @app.get("/items/", tags=["items"])
    async def get_items():
        return [{"name": "wand"}, {"name": "flying broom"}]

    @app.get("/configured-tags", include_in_schema=False)
    async def configured_tags():
        if "cache_mutation" in factory_input:
            schema = app.openapi()
            result = {
                "attribute_exists": hasattr(app, "openapi_tags"),
                "schema_tags": schema.get("tags"),
                "schema_paths": sorted(schema.get("paths", {})),
            }
            if hasattr(app, "openapi_tags"):
                result["attribute"] = app.openapi_tags
            return result
        if "delete_openapi_tags" in factory_input and "replacement_tags" not in factory_input:
            return {"attribute_exists": hasattr(app, "openapi_tags")}
        return {
            "attribute": app.openapi_tags,
            "schema_tags": app.openapi().get("tags"),
        }

    if "cache_mutation" in factory_input:
        app.openapi()
        mutation = factory_input["cache_mutation"]
        if mutation["kind"] == "append":
            tags.append(mutation["tag"])
        elif mutation["kind"] == "replace":
            app.openapi_tags = mutation["tags"]
        elif mutation["kind"] == "delete":
            del app.openapi_tags
        elif mutation["kind"] == "append-and-add-route":
            tags.append(mutation["tag"])

            @app.get("/late-route", tags=["late"])
            async def late_route():
                return {"name": "late"}

    if factory_input.get("generate_openapi_at_construction", False):
        app.openapi()

    return app
