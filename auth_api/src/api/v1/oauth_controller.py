from flask import Blueprint, jsonify, request, json, redirect, url_for

from src.api.v1.utils import validator_json_request, request_has_user_agent
from src.services.oauth_service import get_oauth_service
from src.repositories import token_rep
from src.repositories import oauth_rep
from src.core.config import settings
from src.repositories.oauth import oauth
from src.utils.rate_limit import rate_limit
import requests

oauth_bp = Blueprint("oauth", __name__, url_prefix="/api/v1/oauth")
oauth_rep.create_service(settings.oauth.yandex.dict())


@rate_limit()
@oauth_bp.route("/login")
def login():
    redirect_uri = url_for("oauth.authorize", _external=True)
    return oauth.yandex.authorize_redirect(redirect_uri)


@rate_limit()
@request_has_user_agent
@oauth_bp.route("/authorize")
def authorize():
    oauth_service = get_oauth_service(
        oauth_rep.get_oauth_repository(), token_rep.get_token_repository()
    )
    user_agent = request.headers.get("User-Agent")
    yandex_response = requests.post(
        url=settings.oauth.yandex.access_token_url,
        data={
            "grant_type": "authorization_code",
            "code": request.args.get("code"),
            "client_id": settings.oauth.yandex.client_id,
            "client_secret": settings.oauth.yandex.client_secret,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    ).json()
    token: str = yandex_response["access_token"]
    info = requests.get(
        url=settings.oauth.yandex.get_info_url,
        headers={
            "Authorization": "OAuth " + token,
        },
    ).json()
    social_id: str = info.get("id")
    user_login: str = info.get("login")
    status, result = oauth_service.login_or_create_social(
        social_id, user_login, user_agent
    )

    return jsonify(result), status
