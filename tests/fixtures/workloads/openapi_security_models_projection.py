"""Input-only argument bundles for direct OpenAPI security model probes."""

from __future__ import annotations


def create_argument_bundles() -> dict[str, dict[str, object]]:
    flows = {
        "implicit": {
            "authorizationUrl": "authorization endpoint",
            "scopes": {"read": "Read records"},
        },
        "password": {
            "tokenUrl": "password token endpoint",
            "refreshUrl": "refresh endpoint",
        },
        "clientCredentials": {
            "tokenUrl": "client token endpoint",
            "scopes": {"write": "Write records"},
        },
        "authorizationCode": {
            "authorizationUrl": "authorization-code endpoint",
            "tokenUrl": "authorization-code token endpoint",
            "scopes": {"admin": "Manage records"},
        },
    }

    return {
        "unused": {"args": [], "kwargs": {}},
        "http-base-defaults": {
            "args": [],
            "kwargs": {"scheme": "custom-scheme"},
        },
        "http-base-populated": {
            "args": [],
            "kwargs": {
                "type": "http",
                "description": "HTTP authentication",
                "scheme": "mutualTLS",
                "x-model-source": "input-defined",
            },
        },
        "http-base-field-name-type": {
            "args": [],
            "kwargs": {"type_": "oauth2", "scheme": "custom-scheme"},
        },
        "http-base-missing-scheme": {"args": [], "kwargs": {}},
        "http-base-invalid-type": {
            "args": [],
            "kwargs": {"type": "unsupported", "scheme": "custom-scheme"},
        },
        "http-bearer-defaults": {"args": [], "kwargs": {}},
        "http-bearer-populated": {
            "args": [],
            "kwargs": {
                "type": "http",
                "description": "Bearer authentication",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "x-model-source": "input-defined",
            },
        },
        "http-bearer-invalid-scheme": {
            "args": [],
            "kwargs": {"scheme": "basic"},
        },
        "oauth-flow-defaults": {"args": [], "kwargs": {}},
        "oauth-flow-populated": {
            "args": [],
            "kwargs": {
                "refreshUrl": "refresh endpoint",
                "scopes": {"read": "Read records", "write": "Write records"},
                "x-flow-source": "input-defined",
            },
        },
        "oauth-flow-implicit-minimal": {
            "args": [],
            "kwargs": {"authorizationUrl": "authorization endpoint"},
        },
        "oauth-flow-implicit-populated": {
            "args": [],
            "kwargs": {
                "authorizationUrl": "authorization endpoint",
                "refreshUrl": "refresh endpoint",
                "scopes": {"read": "Read records"},
            },
        },
        "oauth-flow-implicit-missing": {"args": [], "kwargs": {}},
        "oauth-flow-password-minimal": {
            "args": [],
            "kwargs": {"tokenUrl": "token endpoint"},
        },
        "oauth-flow-password-populated": {
            "args": [],
            "kwargs": {
                "tokenUrl": "token endpoint",
                "refreshUrl": "refresh endpoint",
                "scopes": {"read": "Read records"},
            },
        },
        "oauth-flow-password-missing": {"args": [], "kwargs": {}},
        "oauth-flow-client-credentials-minimal": {
            "args": [],
            "kwargs": {"tokenUrl": "token endpoint"},
        },
        "oauth-flow-client-credentials-populated": {
            "args": [],
            "kwargs": {
                "tokenUrl": "token endpoint",
                "refreshUrl": "refresh endpoint",
                "scopes": {"write": "Write records"},
            },
        },
        "oauth-flow-client-credentials-missing": {"args": [], "kwargs": {}},
        "oauth-flow-authorization-code-minimal": {
            "args": [],
            "kwargs": {
                "authorizationUrl": "authorization endpoint",
                "tokenUrl": "token endpoint",
            },
        },
        "oauth-flow-authorization-code-populated": {
            "args": [],
            "kwargs": {
                "authorizationUrl": "authorization endpoint",
                "tokenUrl": "token endpoint",
                "refreshUrl": "refresh endpoint",
                "scopes": {"admin": "Manage records"},
            },
        },
        "oauth-flow-authorization-code-missing-authorization-url": {
            "args": [],
            "kwargs": {"tokenUrl": "token endpoint"},
        },
        "oauth-flow-authorization-code-missing-token-url": {
            "args": [],
            "kwargs": {"authorizationUrl": "authorization endpoint"},
        },
        "oauth-flows-defaults": {"args": [], "kwargs": {}},
        "oauth-flows-populated": {
            "args": [],
            "kwargs": {
                **flows,
                "x-flows-source": "input-defined",
            },
        },
        "oauth2-defaults": {"args": [], "kwargs": {"flows": {}}},
        "oauth2-populated": {
            "args": [],
            "kwargs": {
                "type": "oauth2",
                "description": "OAuth 2 authentication",
                "flows": flows,
                "x-model-source": "input-defined",
            },
        },
        "oauth2-missing-flows": {"args": [], "kwargs": {}},
        "open-id-connect-defaults": {
            "args": [],
            "kwargs": {"openIdConnectUrl": "not URL constrained"},
        },
        "open-id-connect-populated": {
            "args": [],
            "kwargs": {
                "type": "openIdConnect",
                "description": "OpenID Connect authentication",
                "openIdConnectUrl": "https://issuer.example.test/.well-known/openid-configuration",
                "x-model-source": "input-defined",
            },
        },
        "open-id-connect-missing-url": {"args": [], "kwargs": {}},
        "components-security-schemes": {
            "args": [],
            "kwargs": {
                "securitySchemes": {
                    "ApiKey": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-Key",
                    },
                    "HttpBase": {
                        "type": "http",
                        "scheme": "basic",
                    },
                    # HTTPBase requires scheme; this input exercises HTTPBearer's default.
                    "HttpBearer": {
                        "type": "http",
                        "bearerFormat": "JWT",
                    },
                    "OAuth2": {"type": "oauth2", "flows": flows},
                    "OpenIdConnect": {
                        "type": "openIdConnect",
                        "openIdConnectUrl": "https://issuer.example.test/configuration",
                    },
                    "Reference": {"$ref": "#/components/securitySchemes/ApiKey"},
                },
                "x-components-source": "input-defined",
            },
        },
        "components-security-schemes-invalid-http": {
            "args": [],
            "kwargs": {"securitySchemes": {"HttpBase": {"type": "http", "scheme": None}}},
        },
    }
