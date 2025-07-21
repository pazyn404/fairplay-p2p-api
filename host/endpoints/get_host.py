from app import app, db
from models import Host
from decorators import format_response


@app.route("/hosts", methods=["GET"])
@format_response
def get_host() -> tuple[dict, int]:
    host = db.session.query(Host).first()
    return host.data, 200
