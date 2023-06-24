import uuid

ADMIN_USER = {"id": uuid.uuid4(), "login": "super_user", "password": "super_user"}

ADMIN_ROLE = {"id": uuid.uuid4(), "name": "admin"}

ROLE_USER = {
    "id": uuid.uuid4(),
    "user_id": ADMIN_USER.get("id"),
    "role_id": ADMIN_ROLE.get("id"),
}
