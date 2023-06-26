from dawndungeon.db.mongodb.entities.shared.item import Item
from dawndungeon.db.mongodb.entities.character import Character
from dawndungeon.db.mongodb.entities.equipment import Equipment
from dawndungeon import mongodb
from pydantic import BaseModel
from typing import List, Optional
import json


class ItemManager(BaseModel):
    """Util that manages character's items in game."""

    def get_world_items(self, world_id: str) -> Optional[List[Item]]:
        """Gets all items in the world."""
        return mongodb.get_world(world_id).items

    def _get_character(self, session_id: str, character_id: str) -> Character:
        characters: List[Character] = mongodb.get_session(session_id).characters

        try:
            character: Character = next(
                filter(lambda character: character._id == character_id, characters)
            )
        except StopIteration:
            raise ValueError(
                f"Character with id {character_id} not found in session with id {session_id}."
            )

        return character

    def get_character_equipements(
        self, session_id: str, character_id: str
    ) -> Optional[List[Equipment]]:
        """Gets all equipment of the character."""
        character: Character = self._get_character(session_id, character_id)
        return character.inventory

    def set_character_equipments(
        self, session_id: str, character_id: str, new_items: List[Item]
    ) -> None:
        """Sets all equipment of the character."""
        character: Character = self._get_character(session_id, character_id)
        new_equipments: List[Equipment] = [
            Equipment.from_item(**item.dict()) for item in new_items
        ]
        character.inventory = new_equipments

    def update_character_equipment(
        self, session_id: str, character_id: str, equipment: Equipment
    ) -> None:
        """Updates an equipment in the character's inventory."""
        character: Character = self._get_character(session_id, character_id)

        try:
            old_equipment: Equipment = next(
                filter(
                    lambda equipment: equipment._equipment_id
                    == equipment._equipment_id,
                    character.inventory,
                )
            )
        except StopIteration:
            raise ValueError(
                f"Equipment with id {equipment._equipment_id} not found in character's inventory."
            )

        character.inventory.remove(old_equipment)
        character.inventory.append(equipment)

    def add_character_equipment(
        self, session_id: str, character_id: str, item: Item
    ) -> None:
        """Adds a item to the character's inventory."""
        character: Character = self._get_character(session_id, character_id)
        character.inventory.append(Equipment.from_item(**item.dict()))

    def remove_character_equipment(
        self, session_id: str, character_id: str, equipment_id: str
    ) -> None:
        """Removes an equipment from the character's inventory."""
        character: Character = self._get_character(session_id, character_id)

        try:
            equipment: Equipment = next(
                filter(
                    lambda equipment: equipment._equipment_id == equipment_id,
                    character.inventory,
                )
            )
        except StopIteration:
            raise ValueError(
                f"Equipment with id {equipment_id} not found in character's inventory."
            )

        character.inventory.remove(equipment)

    def run(
        self,
        query: str,
    ) -> None:
        """Runs the item manager"""
        args: dict = json.loads(query)
        getattr(self, args["method"])(**args["args"])
