from typing import List
from fastapi import Depends, HTTPException, status
from core.security import get_current_user_tenant
from models.db import User

def check_role(allowed_roles: List[str]):
    async def role_checker(
        current_user: dict = Depends(get_current_user_tenant)
    ):
        # In a real implementation, we would fetch the user from the DB
        # This is a placeholder that assumes the role is in the token or fetched
        user_role = current_user.get("role", "viewer")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

# Helper dependencies
admin_required = check_role(["admin"])
user_required = check_role(["admin", "user"])
viewer_required = check_role(["admin", "user", "viewer"])
