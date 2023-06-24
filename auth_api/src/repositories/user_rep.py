from uuid import UUID

from flask_sqlalchemy import session
from src.models.auth_history import AuthHistory
from src.models.role import Role
from src.models.user import User


class UserRepository:
    def __init__(self, db_session: session):
        self._postgres_session = db_session

    def get_all_users_with_id(self):
        """Get all users with their IDs."""
        users = User.query.all()
        return [{"user_id": user.id, "login": user.login} for user in users]

    def get_user_by_login(self, login: str):
        """Get a user by their login."""
        user = User.query.filter_by(login=login).first()
        if user:
            return {"user_id": user.id, "login": user.login}
        return {"message": "User not found."}

    def assign_role_to_user(self, user_id: str, role_name: str):
        """Assign a role to a user using their IDs."""
        user = User.query.get(user_id)
        role = Role.query.filter_by(name=role_name).first()
        if user and role:
            if role in user.roles:
                return {"message": "Role already assigned to user."}
            user.roles.append(role)
            self._postgres_session.commit()
            return {"message": "Role assigned to user successfully."}
        return {"message": "User or role not found."}

    def revoke_role_from_user(self, user_id: str, role_name: str):
        """Revoke a role from a user using their IDs."""
        user = User.query.get(user_id)
        role = Role.query.filter_by(name=role_name).first()
        if user and role:
            if role in user.roles:
                user.roles.remove(role)
                self._postgres_session.commit()
                return {"message": "Role revoked from user successfully."}
            return {"message": "Role not assigned to user."}
        return {"message": "User or role not found."}

    def get_user_permissions(self, user_id: str):
        """Get all permissions of a user by their ID."""
        user = User.query.get(user_id)
        if user:
            permissions = set()
            for role in user.roles:
                permissions.add(role.name)
            return {
                "user_id": user.id,
                "login": user.login,
                "permissions": list(permissions),
            }
        return {"message": "User not found."}

    def get_user_history(self, user_id: UUID, page_number: int, page_size: int):
        """Get all user's of a user auth by their ID."""
        history = AuthHistory.query.filter_by(user_id=user_id).paginate(
            page=page_number, per_page=page_size, error_out=False
        )
        if history:
            return [
                {
                    "user_id": row.user_id,
                    "user_agent": row.user_agent,
                    "auth_date": row.auth_date,
                }
                for row in history
            ]
        return {"message": "User history is not found"}


user_repository: UserRepository | None = None


def get_user_repository():
    return user_repository
