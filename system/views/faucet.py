from app import app, db
from models import User


@app.route("/faucet/<user_id>", methods=["POST"])
def faucet(user_id):
    user = db.session.get(User, user_id)
    user.balance += 100
    db.session.commit()

    return {200: "ok"}
