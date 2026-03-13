from flask import Blueprint, jsonify, Response

# from assets.core.repository import AssetRepository
# from assets.db.connection import SessionLocal

from asset_common.logging_utils import setup_logger

log = setup_logger("assets")

bp = Blueprint("assets", __name__)

log.info("Initializing asset service routes", extra={"blueprint": bp})

@bp.route("/health", methods=["GET"])
def health() -> Response:
    return jsonify({"status": "ok"})
#
# @bp.route("/assets/<int:id>", methods=["GET"])
# def get_assets(id_: int) -> Response:
#     session = SessionLocal()
#     asset = AssetRepository.get_by_id(session, id_)
#     return jsonify({"name": asset.name}) if asset else jsonify({"message": "Asset not found"}, status=404)