from app import app, db
from config import inflect_engine
from models import User, Host, game_models
from decorators import format_response
from formatters import format_errors


models = {
    "user": User,
    "host": Host,
    **game_models
}


@app.route("/<plural_model_name>/<instance_id>", methods=["GET"])
@format_response
def get(plural_model_name, instance_id):
    model_name = inflect_engine.singular_noun(plural_model_name)
    model = models.get(model_name)
    if not model:
        return format_errors(["Model does not exist"], 400)

    instance = db.session.get(model, instance_id)

    if not instance:
        return format_errors(["Instance not found"], 404)

    return instance.data, 200

