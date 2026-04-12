import asyncio
import pytest
from app.api.v1.dependencies.auth import get_current_user, require_role
from app.core.security import create_access_token
from fastapi import HTTPException


def test_get_current_user_signature_algorithm_mismatch_again():
    token = create_access_token({"sub": "t1", "username": "u1", "roles": ["admin"]})
    # Simulate mismatch by temporarily switching algorithm in security module
    import backend.app.core.security as sec
    old = getattr(sec, 'ALGORITHM', None)
    try:
        if old is not None:
            setattr(sec, 'ALGORITHM', 'HS512')
        with pytest.raises(Exception):
            asyncio.get_event_loop().run_until_complete(get_current_user(db=None, token=token))  # type: ignore
    finally:
        if old is not None:
            setattr(sec, 'ALGORITHM', old)


def test_get_current_user_issuer_and_audience_mismatch_boundaries():
    token = create_access_token({"sub": "t2", "username": "u2", "roles": ["admin"], "iss": "issuer-a", "aud": "aud-a"})
    import os
    os.environ['ISSUER'] = 'issuer-b'
    os.environ['AUDIENCE'] = 'aud-b'
    from app.api.v1.dependencies.auth import get_current_user
    import pytest, asyncio
    with pytest.raises(Exception):
        asyncio.get_event_loop().run_until_complete(get_current_user(db=None, token=token))  # type: ignore
    del os.environ['ISSUER']
    del os.environ['AUDIENCE']


def test_require_role_with_multiple_roles_pass():
    dep = require_role("admin")
    async def run():
        return await dep({"roles": ["admin", "user"]})
    assert asyncio.get_event_loop().run_until_complete(run()) is True


def test_require_role_with_multiple_roles_fail():
    dep = require_role("admin")
    async def run():
        return await dep({"roles": ["user"]})
    with pytest.raises(HTTPException) as exc:
        asyncio.get_event_loop().run_until_complete(run())
    assert exc.value.status_code == 403


def test_require_role_with_empty_roles():
    dep = require_role("admin")
    async def run():
        return await dep({"roles": []})
    with pytest.raises(HTTPException) as exc:
        asyncio.get_event_loop().run_until_complete(run())
    assert exc.value.status_code == 403
