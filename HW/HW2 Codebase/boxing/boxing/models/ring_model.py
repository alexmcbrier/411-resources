import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    """
    A class that manages the fight between boxers in the ring.
    """
    def __init__(self):
        self.ring: List[Boxer] = []
        """Sets the ring as empty, with no boxers currently inside.

        """
    def fight(self) -> str:
        """
        Simulates a fight between two boxers and returns the outcome.

        Returns: 
            str: returns the name of the boxer that won the match.
        
        Raises:
            ValueError: If there are less than 2 boxers in the ring, cannot fight.
        """
        if len(self.ring) < 2:
            raise ValueError("There must be two boxers to start a fight.")

        boxer_1, boxer_2 = self.get_boxers()

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)

        # Compute the absolute skill difference
        # And normalize using a logistic function for better probability scaling
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))

        random_number = get_random()

        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
        else:
            winner = boxer_2
            loser = boxer_1

        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')

        self.clear_ring()

        return winner.name

    def clear_ring(self):
        """
        Clears the boxers from the ring

        Returns: 
            bool: True if the ring was cleared, false if the ring was already empty and nothing needed to be done.
        """
        if not self.ring:
            return
        self.ring.clear()

    def enter_ring(self, boxer: Boxer):
        """
        Allows a boxer to enter the ring, by adding the boxer object to the ring, which is a list of boxers.

        Args:
            Boxer: The boxer object you are adding to the ring

        Returns: 
            bool: bool: True if the ring was cleared, false if the ring was already empty and nothing needed to be done.
        
        Raises:
            TypeError: If the argument supposed to be a boxer object was the wrong type
            ValueError: The ring is full and cannot have more than two boxers.
        """
        if not isinstance(boxer, Boxer):
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)

    def get_boxers(self) -> List[Boxer]:
        if not self.ring:
            pass
        else:
            pass
        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier

        return skill
