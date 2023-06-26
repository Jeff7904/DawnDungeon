
from dawndungeon.api.schemas import PydanticObjectId
from pydantic import BaseModel, root_validator, Field
from bson import ObjectId, json_util
import json
from typing import Union, Optional
from uuid import uuid4

class Session(BaseModel):
    """Individual session of a player.
    """
    # class Config:
    #     allow_population_by_field_name = True
    #     arbitary_types_allowed = True
    #     json_encoders = {ObjectId: str}

    # id_: Union[str, PydanticObjectId] = Field(default_factory=PydanticObjectId, alias='_id')

    # user_id: Union[str, PydanticObjectId] = Field(default_factory=PydanticObjectId, alias='user_id')
    # world_id: Union[str, PydanticObjectId] = Field(default_factory=PydanticObjectId, alias='world_id')
    id_: str = Field(alias='_id', default=None, excluded_none=True)
    _id: str = Field(alias='id', default=None, excluded_none=True)

    user_id: str
    world_id: str


    @root_validator(pre=True)
    def _check_id(cls, values):
        if not 'id_' in values:
            values['_id'] = str(uuid4())
            values['id_'] = values['_id']
        if not 'user_id' in values:
            raise ValueError('user_id is required')
        if not 'world_id' in values:
            raise ValueError('world_id is required')
        return values

    _cls: str = __name__
