from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore

from .db import db
from .user import User
from .role import Role


migrate = Migrate()

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(datastore=user_datastore)
