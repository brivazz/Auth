import logging

import redis
from flask import Flask, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor

from src.api.v1.hello_controller import hello_bp
from src.api.v1.role_controller import role_bp
from src.api.v1.token_controller import token
from src.api.v1.user_controller import user_bp
from src.api.v1.oauth_controller import oauth_bp
from src.core.config import settings
from src.models.db import db
from src.repositories.oauth import oauth
from src.models.utils import security
from src.repositories import token_rep, role_rep, user_rep, oauth_rep
from src.utils.create_superuser import create_superuser
from src.swagger.swagger import swagger_ui_blueprint, SWAGGER_URL


def create_app():
    app = Flask(__name__)

    # App configuration
    app.config["DEBUG"] = settings.debug
    app.config["SECRET_KEY"] = settings.secret_key

    # Configure Flask-SQLAlchemy
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{settings.postgres.user}:{settings.postgres.password}@"
        f"{settings.postgres.host}:{settings.postgres.port}/{settings.postgres.dbname}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # app.config['OAUTH_CREDENTIALS'] = {
    #     'YANDEX': {
    #         'id': settings.yandex_id,
    #         'secret': settings.yandex_secret,
    #     }
    # }

    jwt = JWTManager(app)
    bcrypt = Bcrypt(app)

    redis_db = redis.Redis(host=settings.redis.host, port=settings.redis.port)
    token_rep.token_repository = token_rep.TokenRepository(redis_db, db.session)
    logging.info(f"token repository is: {token_rep.token_repository}")

    role_rep.role_repository = role_rep.RoleRepository(db.session)
    logging.info(f"role repository is: {role_rep.role_repository}")

    user_rep.user_repository = user_rep.UserRepository(db.session)
    logging.info(f"role repository is: {role_rep.role_repository}")

    oauth_rep.oauth_repository = oauth_rep.OAuthRepository(db.session)
    logging.info(f"oauth repository is: {role_rep.role_repository}")

    app.register_blueprint(hello_bp)
    app.register_blueprint(token)
    app.register_blueprint(role_bp)
    app.register_blueprint(oauth_bp)
    app.register_blueprint(user_bp)

    app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

    # Tracer configuration
    if settings.tracer_enabled:
        FlaskInstrumentor().instrument_app(app)

        @app.before_request
        def before_request():
            request_id = request.headers.get("X-Request-Id")
            if not request_id:
                raise RuntimeError("request id is required")

            tracer = trace.get_tracer(__name__, schema_url="http")
            with tracer.start_as_current_span("auth") as span:
                span.set_attribute("http.request_id", request_id)

    # Database initialization
    db.init_app(app)

    migrate = Migrate()
    migrate.init_app(app, db)

    oauth.init_app(app)
    security.init_app(app)
    app.logger.info("Initialized database complete.")

    # register command
    app.cli.add_command(create_superuser)

    return app
