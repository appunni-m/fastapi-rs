"""FastAPI page workflow links requiring independent source selectors."""

DOC_PAGE_CASE_LINK_COMPLETIONS_WAVE_L = {
    "advanced/websockets.md": [
        {
            "recipe_path": "tests/fixtures/input-recipes/parity/websockets-cli-startup.yaml",
            "case_ids": ["fastapi.cli.process.websockets-startup-readiness"],
            "observation_selectors": [
                "http.body.bytes",
                "http.status",
                "process.exit_code",
            ],
            "scope_note": (
                "Partial independent process sample; observes FastAPI CLI startup and HTTP "
                "readiness for an app that declares a WebSocket route. It does not connect "
                "a WebSocket client or claim browser behavior."
            ),
        },
    ]
}
