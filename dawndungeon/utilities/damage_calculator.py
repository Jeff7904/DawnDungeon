"""Util that calculates damage
"""
from pydantic import BaseModel
from typing import Any
import json

class DamageCalculator(BaseModel):
    """Wrapper for Damage Calculator
    """
    def run(
        self,
        query: str,
    ) -> int:
        """Runs the damage calculator
        """
        args: dict = json.loads(query)
        return (args["attacker_damage"] * 2) - args["defender_defense"]
