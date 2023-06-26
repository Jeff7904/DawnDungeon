
from bson import ObjectId, json_util
from typing import Optional, List, Union
from pydantic import BaseModel, Field
from dawndungeon.api.schemas import PydanticObjectId
import json

class World(BaseModel):
    """Environment for the game session.
    """
    # class Config:
    #     allow_population_by_field_name = True
    #     arbitary_types_allowed = True
    #     json_encoders = {ObjectId: str}

    # id_: Union[str, PydanticObjectId] = Field(default_factory=PydanticObjectId, alias='_id')
    id_: str = Field(alias='_id', default=None, excluded_none=True)
    _id: str = Field(alias='id', default=None, excluded_none=True)

    name: str
    description: str

    # items: Optional[List[Item]]
    # enemies: Optional[List[Enemy]]
    # npcs: Optional[List[NPC]]
    # quests: Optional[List[Quest]]

    _cls: str = __name__
