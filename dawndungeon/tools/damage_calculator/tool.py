"""Tool for calculating overall damage of an Entity to an Entity
"""
from dawndungeon.utilities import DamageCalculator
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools.base import BaseTool
from pydantic import Field
from typing import Any, Optional


class DamageCalculatorTool(BaseTool):
    """Tool for calculating overall damage of an Entity to an Entity
    """
    name = "Damage Calculator"
    description = (
        "Useful for when you need to calculate the overall damage of an Entity to an Entity."
        "The input to this tool should be a dictionary with the following keys:"
        "    - attacker_damage: int"
        "    - defender_defense: int"
        "For example,"
        "if you wanted to calculate the overall damage of an Entity with 10 attack to an Entity with 5 defense,"
        "you would input:"
        "{\"attacker_damage\": 10, \"defender_defense\": 5}"
        "The output of this tool will be an int representing the overall damage."
    )
    damage_calculator: DamageCalculator = Field(default_factory=DamageCalculator)

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> int:
        """Runs the tool
        """
        damage: int = self.damage_calculator.run(query)
        return damage

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> Any:
        """Runs the tool asynchronously
        """
        raise NotImplementedError("DamageCalculator does not support async.")
