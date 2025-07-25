from app import app, db
from models import User
from decorators import format_response


@app.route("/users", methods=["GET"])
@format_response
def get_user() -> tuple[dict, int]:
    user = db.session.query(User).first()
    return user.data, 200
