import asyncio
import pytest
from datetime import timedelta
from app.api.v1.dependencies.auth import get_current_user, require_role
from app.core.security import create_access_token
from fastapi import HTTPException


def test_get_current_user_valid():
    payload = {"sub": "user-1", "username": "alice", "roles": ["admin"]}
    token = create_access_token(payload)
    user = asyncio.get_event_loop().run_until_complete(get_current_user(db=None, token=token))  # type: ignore
    assert user["id"] == payload["sub"]
    assert user["username"] == payload["username"]
    assert "admin" in user["roles"]


def test_get_current_user_invalid():
    with pytest.raises(HTTPException) as exc:
        asyncio.get_event_loop().run_until_complete(get_current_user(db=None, token="not-a-jwt"))  # type: ignore
    assert exc.value.status_code == 401


def test_get_current_user_expired():
    payload = {"sub": "user-1", "username": "alice", "roles": ["admin"]}
    expired = create_access_token(payload, expires_delta=timedelta(minutes=-5))
    with pytest.raises(HTTPException) as exc:
        asyncio.get_event_loop().run_until_complete(get_current_user(db=None, token=expired))  # type: ignore
    assert exc.value.status_code == 401


def test_missing_authorization_header():
    with pytest.raises(HTTPException) as exc:
        asyncio.get_event_loop().run_until_complete(get_current_user(db=None, token=None))  # type: ignore
    assert exc.value.status_code == 401


def test_require_role_admin_pass():
    dep = require_role("admin")
    async def run():
        return await dep({"roles": ["admin"]})
    assert asyncio.get_event_loop().run_until_complete(run()) is True


def test_require_role_admin_fail():
    dep = require_role("admin")
    async def run():
        return await dep({"roles": ["user"]})
    with pytest.raises(HTTPException) as exc:
        asyncio.get_event_loop().run_until_complete(run())
    assert exc.value.status_code == 403


def test_require_role_missing_roles():
    dep = require_role("admin")
    async def run():
        return await dep({})
    with pytest.raises(HTTPException) as exc:
        asyncio.get_event_loop().run_until_complete(run())
    assert exc.value.status_code == 403


def test_get_current_user_signature_mismatch():
    # Create a valid token with current SECRET_KEY
    from app.core.security import create_access_token
    import backend.app.core.security as sec  # type: ignore
    import os
    import pytest
    token = create_access_token({"sub": "user-sig", "username": "siguser", "roles": ["admin"]})
    old_key = sec.SECRET_KEY
    try:
        sec.SECRET_KEY = "DIFFERENT"
        from app.api.v1.dependencies.auth import get_current_user
        with pytest.raises(Exception):
            # Expect a 401-like JWT decode error leading to an HTTPException in real path
            # We call the function directly; will raise HTTPException due to invalid signature
            import asyncio
            asyncio.get_event_loop().run_until_complete(get_current_user(db=None, token=token))  # type: ignore
    finally:
        sec.SECRET_KEY = old_key


def test_get_current_user_issuer_mismatch():
    # Create a token with issuer and ensure issuer mismatch is detected
    token = create_access_token({"sub": "issuer-user", "username": "issuer", "roles": ["admin"], "iss": "trusted-issuer"})
    import os
    os.environ["ISSUER"] = "expected-issuer"
    from app.api.v1.dependencies.auth import get_current_user
    import pytest, asyncio
    with pytest.raises(Exception):
        asyncio.get_event_loop().run_until_complete(get_current_user(db=None, token=token))  # type: ignore
    del os.environ["ISSUER"]

def test_get_current_user_signature_algorithm_mismatch(monkeypatch):
    # Create a valid token with current SECRET_KEY; then change the decoding algorithm to simulate mismatch
    from app.core.security import create_access_token
    import backend.app.core.security as sec
    token = create_access_token({"sub": "probe-user", "username": "probe", "roles": ["admin"]})
    old_alg = getattr(sec, "ALGORITHM", None)
    try:
        if old_alg is not None:
            setattr(sec, "ALGORITHM", "HS512")  # simulate mismatch
            from app.api.v1.dependencies.auth import get_current_user
            import pytest, asyncio
            with pytest.raises(Exception):
                asyncio.get_event_loop().run_until_complete(get_current_user(db=None, token=token))  # type: ignore
    finally:
        if old_alg is not None:
            setattr(sec, "ALGORITHM", old_alg)

def test_get_current_user_wrong_audience(monkeypatch):
    # Ensure AUDIENCE env is set to a value that token must satisfy
    import os
    os.environ["AUDIENCE"] = "correct-aud"
    # Create a token with wrong aud by embedding aud in payload and signing with SECRET_KEY
    from app.core.security import create_access_token
    payload = {"sub": "user-aud", "username": "aud_user", "roles": ["admin"], "aud": "wrong-aud"}
    token = create_access_token(payload)
    with pytest.raises(HTTPException) as exc:
        asyncio.get_event_loop().run_until_complete(get_current_user(db=None, token=token))  # type: ignore
    assert exc.value.status_code == 401
    del os.environ["AUDIENCE"]


def test_get_current_user_audience_mismatch():
    from app.core.security import create_access_token
    token = create_access_token({"sub": "aud-mismatch2", "username": "tester", "roles": ["admin"], "aud": "aud-1"})
    import os
    os.environ["AUDIENCE"] = "aud-2"
    from app.api.v1.dependencies.auth import get_current_user
    import pytest, asyncio
    with pytest.raises(Exception):
        asyncio.get_event_loop().run_until_complete(get_current_user(db=None, token=token))  # type: ignore
    del os.environ["AUDIENCE"]


def test_require_role_with_multiple_roles_pass():
    dep = require_role("admin")
    async def run():
        return await dep({"roles": ["admin", "user"]})
    assert asyncio.get_event_loop().run_until_complete(run()) is True
