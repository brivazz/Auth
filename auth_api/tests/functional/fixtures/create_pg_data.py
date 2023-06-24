import bcrypt
import pytest
import pytest_asyncio
import sqlalchemy
from sqlalchemy import create_engine, text

from functional.settings import test_settings
from functional.testdata.pg_data import ADMIN_USER, ADMIN_ROLE, ROLE_USER


@pytest.fixture(scope="session")
def pg_engine():
    engine = create_engine(
        f"postgresql://{test_settings.pg_user}:"
        f"{test_settings.pg_password}@{test_settings.pg_host}"
        f":{test_settings.pg_port}/{test_settings.dbname}"
    )
    yield engine


@pytest.fixture(scope="session", autouse=True)
def delete_all_pg_data(pg_engine: sqlalchemy.Engine):
    def delete(engine):
        table_names = [
            "auth_history",
            "user_role",
            "roles",
            "users",
        ]

        with engine.begin() as connection:
            for table in table_names:
                query = text(f"TRUNCATE {table} RESTART IDENTITY CASCADE;")
                connection.execute(query)

    delete(pg_engine)
    yield
    delete(pg_engine)


@pytest_asyncio.fixture(scope="session")
async def admin_tokens(make_get_request, pg_engine: sqlalchemy.Engine):
    salt = bcrypt.gensalt()
    test_user_password = ADMIN_USER.get("password").encode("utf-8")
    hashed_password = bcrypt.hashpw(test_user_password, salt)
    requests = [
        (
            "INSERT INTO users(id, login, password) \
                VALUES (:id, :login, :password);",
            {
                "id": ADMIN_USER.get("id"),
                "login": ADMIN_USER.get("login"),
                "password": hashed_password,
            },
        ),
        (
            "INSERT INTO roles(id, name) VALUES (:id, :name);",
            {"id": ADMIN_ROLE.get("id"), "name": ADMIN_ROLE.get("name")},
        ),
        (
            "INSERT INTO user_role(id, user_id, role_id) \
                VALUES (:id, :user_id, :role_id);",
            {
                "id": ROLE_USER.get("id"),
                "user_id": ROLE_USER.get("user_id"),
                "role_id": ROLE_USER.get("role_id"),
            },
        ),
    ]
    with pg_engine.begin() as connection:
        for query, params in requests:
            connection.execute(text(query), params)

    reg_body, reg_status = await make_get_request(
        test_settings.service_url + "/api/v1/auth/login",
        method="POST",
        data={"login": ADMIN_USER.get("login"), "password": ADMIN_USER.get("password")},
    )
    yield reg_body
