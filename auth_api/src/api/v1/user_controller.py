from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from pydantic import BaseModel, constr

from src.repositories import user_rep
from src.services.user_service import get_user_service

from .utils import validator_json_request, check_user_has_role
from src.utils.rate_limit import rate_limit

user_bp = Blueprint("user", __name__, url_prefix="/api/v1/auth")


class RoleValidator(BaseModel):
    role_name: constr(max_length=30)


@user_bp.route("/users/<login>", methods=["GET"])
@rate_limit()
@jwt_required()
@check_user_has_role("admin")
def get_user(login):
    user_service = get_user_service(user_rep.get_user_repository())
    response = user_service.get_user(login=login)
    return jsonify(response)


@user_bp.route("/users/<user_id>/assign-role", methods=["POST"])
@rate_limit()
@jwt_required()
@check_user_has_role("admin")
@validator_json_request(RoleValidator)
def assign_role(body: RoleValidator, user_id):
    user_service = get_user_service(user_rep.get_user_repository())
    params = body.dict()
    response = user_service.assign_role(user_id=user_id, **params)
    return jsonify(response)


@user_bp.route("/users/<user_id>/revoke-role", methods=["POST"])
@rate_limit()
@jwt_required()
@check_user_has_role("admin")
@validator_json_request(RoleValidator)
def revoke_role(body: RoleValidator, user_id):
    user_service = get_user_service(user_rep.get_user_repository())
    params = body.dict()
    response = user_service.revoke_role(user_id=user_id, **params)
    return jsonify(response)


@user_bp.route("/users/<user_id>/check-permissions", methods=["GET"])
@rate_limit()
@jwt_required()
@check_user_has_role("admin")
def check_role(user_id):
    user_service = get_user_service(user_rep.get_user_repository())
    roles = user_service.viewing_role(user_id=user_id)
    return jsonify(roles)


@user_bp.route("/users/<user_id>/history", methods=["GET"])
@rate_limit()
@jwt_required()
@check_user_has_role("admin")
def user_history(user_id):
    user_service = get_user_service(user_rep.get_user_repository())

    page_number = request.args.get("page_number", default=1, type=int)
    page_size = request.args.get("page_size", default=50, type=int)

    if not (100 > page_size > 0):
        return jsonify({"err_msg": "Page size is not valid"}), HTTPStatus.BAD_REQUEST
    if not (100 > page_number > 0):
        return jsonify({"err_msg": "Page number is not valid"}), HTTPStatus.BAD_REQUEST

    history = user_service.user_history(
        user_id=user_id, page_number=page_number, page_size=page_size
    )
    return jsonify(history)
