import uuid

from sqlalchemy.dialects.postgresql import UUID
from flask_security import UserMixin
from sqlalchemy.orm import relationship

from .user_role import user_role_table
from .db import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    login = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)
    roles = relationship(
        "Role", secondary=user_role_table, back_populates="users", passive_deletes="all"
    )

    def __repr__(self):
        return f"<User {self.login}>"
