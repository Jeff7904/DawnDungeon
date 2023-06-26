
from pydantic import BaseModel, root_validator, Field
from dawndungeon.api.schemas import PydanticObjectId
from bson import ObjectId, json_util
from typing import Optional, Union
import json


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    # class Config:
    #     allow_population_by_field_name = True
    #     arbitary_types_allowed = True
    #     json_encoders = {ObjectId: str}

    # id_: Union[str, PydanticObjectId] = Field(default_factory=PydanticObjectId, alias='_id')
    id_: str = Field(alias='_id', default=None, excluded_none=True)
    _id: str = Field(alias='id', default=None, excluded_none=True)
    hashed_password: Optional[str]

    def hidden(self) -> "UserInDB":
        self.hashed_password = None
        return self
