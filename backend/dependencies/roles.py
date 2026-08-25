from fastapi import Depends, HTTPException, status

from dependencies.auth import get_current_user
from models.user import User


def require_role(*allowed_roles: str):
    def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:

        user_role = (
            current_user.role.value
            if hasattr(current_user.role, "value")
            else str(current_user.role)
        )

        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )

        return current_user

    return role_checker