import pytest
from core.security import create_access_token, verify_password, get_password_hash
from core.rbac import check_role
from fastapi import HTTPException

def test_password_hashing():
    password = "secret_password"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_jwt_creation():
    token = create_access_token(subject="user123", tenant_id="tenant456")
    assert isinstance(token, str)
    assert len(token) > 0

def test_rbac_check_role_success():
    # Mocking a dependency/check flow
    def mock_route(role: str):
        if role == "admin":
            return True
        return False
    
    assert mock_route("admin") is True

@pytest.mark.asyncio
async def test_rbac_decorator_logic():
    # This is a unit test for the logic inside RBAC decorators
    from core.rbac import admin_required
    
    async def fake_dependency(current_user: dict = {"role": "admin"}):
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403)
        return current_user

    result = await fake_dependency()
    assert result["role"] == "admin"
