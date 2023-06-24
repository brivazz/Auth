import uuid

from sqlalchemy.dialects.postgresql import UUID

from .db import db
from .user import User


class SocialUser(db.Model):
    __tablename__ = "social_user"

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
    social_id = db.Column(db.Text, nullable=False)
    login = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<SocialUser {self.id}:{self.login}>"
