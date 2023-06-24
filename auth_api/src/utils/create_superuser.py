import datetime

import click
from flask.cli import with_appcontext

from src import db
from src.models.user import User
from src.models.role import Role
from src.utils.extensions import create_hash


@click.command("create_superuser")
@click.option("--login", prompt=True, help="Login for the superuser")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="Password for the superuser",
)
@with_appcontext
def create_superuser(login, password):
    admin_role = Role.query.filter_by(name="admin").first()
    if not admin_role:
        admin_role = Role(name="admin", created=datetime.datetime.now())

    pass_hash = create_hash(password)
    super_user = User(login=login, password=pass_hash, roles=[admin_role])
    db.session.add(super_user)
    db.session.commit()
    return "Superuser created"
