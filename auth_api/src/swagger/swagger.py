import os

from flask import send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint


# Определите путь к вашему OpenAPI-файлу
SWAGGER_URL = "/api/v1/auth/openapi"
API_URL = "./openapi.yaml"  # Путь к вашему OpenAPI-файлу

# Создайте конфигурацию Swagger UI
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Auth Swagger UI"}
)


@swagger_ui_blueprint.route("/openapi.yaml", methods=["GET"])
def send_api_spec():
    current_directory = os.getcwd()
    swagger_directory = os.path.join(current_directory, "src", "swagger")
    return send_from_directory(swagger_directory, "openapi.yaml")
