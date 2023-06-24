from http import HTTPStatus

from flask import Blueprint, jsonify, request, json
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import BaseModel, constr

from src.api.v1.utils import validator_json_request, request_has_user_agent
from src.services.token_service import get_token_service
from src.repositories import token_rep
from src.utils.rate_limit import rate_limit


token = Blueprint("token", __name__, url_prefix="/api/v1/auth")


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


@token.route("/change-password", methods=["POST"])
@rate_limit()
@jwt_required()
@validator_json_request(ChangePasswordRequest)
def change_password(body: ChangePasswordRequest):
    token_service = get_token_service(token_rep.get_token_repository())
    token_inf = json.loads(get_jwt_identity())
    http_status, response_msg = token_service.change_password(
        token_inf, body.old_password, body.new_password
    )
    return jsonify(response_msg), http_status


class LoginRequest(BaseModel):
    login: constr(max_length=50)
    password: str


@token.route("/login", methods=["POST"])
@rate_limit()
@validator_json_request(LoginRequest)
def login(body: LoginRequest):
    token_service = get_token_service(token_rep.get_token_repository())
    user_agent = request.headers.get("User-Agent")
    if len(user_agent) > 300:
        return jsonify({"err_msg": "Incorrect headers"}), HTTPStatus.BAD_REQUEST
    http_status, response_msg = token_service.login(
        body.login, body.password, user_agent
    )
    return jsonify(response_msg), http_status


@token.route("/is_authenticated", methods=["GET"])
@jwt_required()
def is_authenticated():
    response_msg = {"msg": "ok"}
    return jsonify(response_msg), HTTPStatus.OK


class LogoutRequest(BaseModel):
    refresh_token: str


@token.route("/logout", methods=["POST"])
@rate_limit()
@validator_json_request(LogoutRequest)
def logout(body: LogoutRequest):
    token_service = get_token_service(token_rep.get_token_repository())
    http_status, response_msg = token_service.logout(body.refresh_token)
    return jsonify(response_msg), http_status


class ReworkTokensRequest(BaseModel):
    refresh_token: str


@token.route("/refresh-tokens", methods=["POST"])
@rate_limit()
@validator_json_request(ReworkTokensRequest)
def refresh_tokens(body: ReworkTokensRequest):
    token_service = get_token_service(token_rep.get_token_repository())
    http_status, response_msg = token_service.refresh_tokens(body.refresh_token)
    return jsonify(response_msg), http_status


class RegisterRequest(BaseModel):
    login: constr(max_length=50)
    password: str


@token.route("/register", methods=["POST"])
@rate_limit()
@validator_json_request(RegisterRequest)
@request_has_user_agent
def register(body: RegisterRequest):
    token_service = get_token_service(token_rep.get_token_repository())
    user_agent = request.headers.get("User-Agent")
    if len(user_agent) > 300:
        return jsonify({"err_msg": "Incorrect headers"}), HTTPStatus.BAD_REQUEST
    http_status, response_msg = token_service.register(
        body.login, body.password, user_agent
    )
    return jsonify(response_msg), http_status
