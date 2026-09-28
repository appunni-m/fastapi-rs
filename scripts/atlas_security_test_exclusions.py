"""Source-backed exclusions for app-specific crypto branches in security tutorials.

Successful form, OAuth2 bearer, scope, item, and OpenAPI cases stay eligible;
these exclusions are limited to password-authentication and JWT validation
branches that require tutorial-owned pwdlib/PyJWT behavior.
"""

TEST_FUNCTION_EXCLUSIONS = {
    "tests/test_tutorial/test_security/test_tutorial004.py": {
        "test_login_incorrect_password": (
            "Exercises the tutorial's pwdlib password verification and its app-owned "
            "credential failure; FastAPI form binding and successful login are covered "
            "by the synthetic-token workflow."
        ),
        "test_login_incorrect_username": (
            "Exercises the tutorial's pwdlib dummy-hash verification and app-owned user "
            "lookup failure; FastAPI form binding and successful login are covered by "
            "the synthetic-token workflow."
        ),
        "test_incorrect_token": (
            "Exercises the tutorial's PyJWT decode failure and app-owned credentials "
            "exception. It does not test FastAPI bearer extraction; that remains eligible."
        ),
        "test_token_no_sub": (
            "Exercises PyJWT decoding plus the tutorial's app-owned missing-subject "
            "rejection, outside FastAPI's bearer and dependency contract."
        ),
        "test_token_no_username": (
            "Exercises PyJWT decoding and lookup of a subject absent from the tutorial's "
            "user database, outside FastAPI's bearer and dependency contract."
        ),
        "test_token_nonexistent_user": (
            "Exercises PyJWT decoding and tutorial-owned user-database rejection, outside "
            "FastAPI's bearer and dependency contract."
        ),
        "test_token_inactive_user": (
            "Exercises pwdlib password verification, PyJWT issuance, and the tutorial's "
            "app-owned inactive-user rule; it is not a FastAPI security primitive."
        ),
    },
    "tests/test_tutorial/test_security/test_tutorial005.py": {
        "test_login_incorrect_password": (
            "Exercises the tutorial's pwdlib password verification and its app-owned "
            "credential failure; FastAPI form binding and successful login are covered "
            "by the synthetic-token workflow."
        ),
        "test_login_incorrect_username": (
            "Exercises the tutorial's pwdlib dummy-hash verification and app-owned user "
            "lookup failure; FastAPI form binding and successful login are covered by "
            "the synthetic-token workflow."
        ),
        "test_incorrect_token": (
            "Exercises the tutorial's PyJWT decode failure and app-owned credentials "
            "exception. It does not test FastAPI bearer extraction; that remains eligible."
        ),
        "test_token_no_sub": (
            "Exercises PyJWT decoding plus the tutorial's app-owned missing-subject "
            "rejection, outside FastAPI's bearer and dependency contract."
        ),
        "test_token_no_username": (
            "Exercises PyJWT decoding and lookup of a subject absent from the tutorial's "
            "user database, outside FastAPI's bearer and dependency contract."
        ),
        "test_token_nonexistent_user": (
            "Exercises PyJWT decoding and tutorial-owned user-database rejection, outside "
            "FastAPI's bearer and dependency contract."
        ),
        "test_token_inactive_user": (
            "Exercises pwdlib password verification, PyJWT issuance, and the tutorial's "
            "app-owned inactive-user rule; it is not a FastAPI security primitive."
        ),
    },
}


_TEST_DEPENDENCY_EVIDENCE = {
    "path": "pyproject.toml",
    "start_line": 160,
    "end_line": 169,
    "role": "FastAPI's test dependency group declares pwdlib[argon2] and PyJWT",
}


def _source_span(
    path: str,
    start_line: int,
    end_line: int,
    role: str,
) -> dict[str, object]:
    return {
        "path": path,
        "start_line": start_line,
        "end_line": end_line,
        "role": role,
    }


_AUTH_EVIDENCE = {
    "tutorial004": {
        "path": "docs_src/security/tutorial004_py310.py",
        "login": (
            (57, 78, "pwdlib password verification and app-owned credential lookup"),
            (118, 133, "login route invokes app-owned authentication and creates a JWT"),
        ),
        "jwt": ((92, 109, "PyJWT decode and tutorial user-database validation"),),
        "inactive": (
            (112, 115, "tutorial-owned inactive-user rule"),
            (118, 133, "password-authenticated JWT issuance"),
        ),
    },
    "tutorial005": {
        "path": "docs_src/security/tutorial005_py310.py",
        "login": (
            (72, 93, "pwdlib password verification and app-owned credential lookup"),
            (150, 162, "login route invokes app-owned authentication and creates a JWT"),
        ),
        "jwt": ((107, 139, "PyJWT decode and tutorial user-database validation"),),
        "inactive": (
            (142, 147, "tutorial-owned inactive-user rule"),
            (150, 162, "password-authenticated JWT issuance"),
        ),
    },
}


def _evidence_for(tutorial: str, branch: str) -> list[dict[str, object]]:
    path = _AUTH_EVIDENCE[tutorial]["path"]
    evidence: list[dict[str, object]] = []
    for start, end, role in _AUTH_EVIDENCE[tutorial][branch]:
        evidence.append(_source_span(path, start, end, role))
    evidence.append(dict(_TEST_DEPENDENCY_EVIDENCE))
    return evidence


_TUTORIAL_EXCLUSION_PATHS = {
    "tutorial004": "tests/test_tutorial/test_security/test_tutorial004.py",
    "tutorial005": "tests/test_tutorial/test_security/test_tutorial005.py",
}

_EXCLUSION_BRANCH = {
    "test_login_incorrect_password": "login",
    "test_login_incorrect_username": "login",
    "test_incorrect_token": "jwt",
    "test_token_no_sub": "jwt",
    "test_token_no_username": "jwt",
    "test_token_nonexistent_user": "jwt",
    "test_token_inactive_user": "inactive",
}


TEST_FUNCTION_EXCLUSION_EVIDENCE = {
    path: {
        name: _evidence_for(tutorial, _EXCLUSION_BRANCH[name])
        for name in TEST_FUNCTION_EXCLUSIONS[path]
    }
    for tutorial, path in _TUTORIAL_EXCLUSION_PATHS.items()
}
