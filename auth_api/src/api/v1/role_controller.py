from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from pydantic import BaseModel, constr

from src.services.role_service import get_role_service
from src.repositories import role_rep
from src.utils.rate_limit import rate_limit
from .utils import validator_json_request, check_user_has_role


role_bp = Blueprint("role", __name__, url_prefix="/api/v1/auth")


class ValidatorJsonPostDelete(BaseModel):
    name: constr(max_length=30)


class ValidatorJsonUpdate(BaseModel):
    name: str
    new_name: constr(max_length=30)


@role_bp.route("/roles", methods=["POST"])
@rate_limit()
@jwt_required()
@check_user_has_role("admin")
@validator_json_request(ValidatorJsonPostDelete)
def role_create(body: ValidatorJsonPostDelete):
    role_service = get_role_service(role_rep.get_role_repository())
    new_role = role_service.create_role(body.name)
    return jsonify(new_role)


@role_bp.route("/roles/delete", methods=["DELETE"])
@rate_limit()
@jwt_required()
@check_user_has_role("admin")
@validator_json_request(ValidatorJsonPostDelete)
def role_delete(body: ValidatorJsonPostDelete):
    role_service = get_role_service(role_rep.get_role_repository())
    response = role_service.delete_role(body.name)
    return jsonify(response)


@role_bp.route("/roles/update", methods=["PUT"])
@rate_limit()
@jwt_required()
@check_user_has_role("admin")
@validator_json_request(ValidatorJsonUpdate)
def role_update(body: ValidatorJsonUpdate):
    role_service = get_role_service(role_rep.get_role_repository())
    response = role_service.update_role(name=body.name, new_name=body.new_name)
    return jsonify(response)


@role_bp.route("/roles/view", methods=["GET"])
@rate_limit()
@jwt_required()
@check_user_has_role("admin")
def roles_viewed():
    role_service = get_role_service(role_rep.get_role_repository())
    response = role_service.viewing_roles()
    return jsonify(response)
