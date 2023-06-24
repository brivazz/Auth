import uuid
from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID
from flask_security import RoleMixin
from sqlalchemy.orm import relationship

from .user_role import user_role_table
from .db import db


class Role(db.Model, RoleMixin):
    __tablename__ = "roles"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = db.Column(db.String(30), unique=True, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow())
    users = relationship(
        "User", secondary=user_role_table, back_populates="roles", passive_deletes="all"
    )

    def __repr__(self):
        return f"<Role {self.id}:{self.name}>"
