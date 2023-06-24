import logging
import uuid
from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import UniqueConstraint

from .db import db
from .user import User


def create_partition(target, connection, **kw) -> None:
    """creating partition by auth_history_in"""
    logging.info("создание таблиц ура ура ура" * 10)
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "auth_history_in_smart"
        PARTITION OF "auth_history" FOR VALUES IN ('smart')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "auth_history_in_mobile"
        PARTITION OF "auth_history" FOR VALUES IN ('mobile')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "auth_history_in_web"
        PARTITION OF "auth_history" FOR VALUES IN ('web')"""
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS "auth_history_in_api_client"
        PARTITION OF "auth_history" FOR VALUES IN ('api_client')
        """
    )


class AuthHistory(db.Model):
    __tablename__ = "auth_history"
    __table_args__ = (
        UniqueConstraint("id", "user_device_type"),
        {
            "postgresql_partition_by": "LIST (user_device_type)",
            "listeners": [("after_create", create_partition)],
        },
    )

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey(User.id, ondelete="CASCADE"), nullable=False
    )
    user_agent = db.Column(db.String(300))
    user_device_type = db.Column(db.Text, primary_key=True)
    auth_date = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return f"<AuthHistory {self.user_id}:{self.auth_date}>"
