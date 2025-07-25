from app import app, db
from models import User


@app.route("/faucet", methods=["POST"])
def faucet() -> dict:
    user = db.session.query(User).first()
    user.balance += 100
    db.session.commit()

    return {200: "ok"}
