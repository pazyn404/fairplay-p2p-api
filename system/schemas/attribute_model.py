from pydantic import BaseModel


class AttributeModel(BaseModel):
    model_config = {
        "from_attributes": True
    }
