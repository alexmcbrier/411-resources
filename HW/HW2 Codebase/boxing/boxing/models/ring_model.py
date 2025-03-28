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
        """
        Initializes an empty boxing ring.
        """
        logger.info("The ring has been set to empty with no boxers inside")
        self.ring: List[Boxer] = []

    def fight(self) -> str:
        """
        Simulates a fight between two boxers and returns the outcome.

        Returns: 
            str: returns the name of the boxer that won the match.
        
        Raises:
            ValueError: If there are less than 2 boxers in the ring, cannot fight.
        """
        logger.info("Received request to simulate a fight between 2 boxers")
        if len(self.ring) < 2:
            logger.error("There must be two boxers to start a fight.")
            raise ValueError("There must be two boxers to start a fight.")

        boxer_1, boxer_2 = self.get_boxers()
        logger.info("Both boxer objects have been assigned to boxer_1, boxer_2")
        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)
        logger.info("Both boxers have established their fighting skills")
        # Compute the absolute skill difference
        # And normalize using a logistic function for better probability scaling
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))

        random_number = get_random()

        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
            logger.info("Boxer 1 has won the fight, boxer 2 has lost")
        else:
            winner = boxer_2
            loser = boxer_1
            logger.info("Boxer 2 has won the fight, boxer 1 has lost")

        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')
        logger.info("The stats have been updated (win / loss) for both boxers in the database")

        self.clear_ring()
        logger.info("The ring has been succesfuly cleared")
        logger.info("The name of the winning boxer has been returned")
        return winner.name

    def clear_ring(self):
        """
        Clears the boxers from the ring

        Returns: 
            bool: True if the ring was cleared, false if the ring was already empty and nothing needed to be done.
        """
        logger.info("Received request to clear the ring of all boxers")
        if not self.ring:
            logger.warning("The ring was already empty so nothing has been done")
            return
        logger.info("The ring has been succesfuly cleared")
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
        logger.info(f"Received request to have {boxer} enter the ring")
        if not isinstance(boxer, Boxer):
            logger.error(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            logger.warning(f"Ring is full, cannot add more boxers.")
            raise ValueError("Ring is full, cannot add more boxers.")

        logger.info(f"{boxer} has succesfuly entered the ring.")
        self.ring.append(boxer)

    def get_boxers(self) -> List[Boxer]:
        """
        Retrieves the current list of boxers in the ring.

        Returns:
            List[Boxer]: A list of boxer objects currently in the ring (maximum of 2)
        """
        if not self.ring:
            pass
        else:
            pass
        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """
        Calculates a boxer's fighting skill based on weight, reach, age, and name length.

        The skill is computed with the formula: 
            skill = (weight * name_length) + (reach / 10) + age_modifier

        - name_length is the number of characters in the boxer's name.
        - reach is divided by 10 to reduce its scale.
        - age_modifier is:
            - -1 if age < 25
            -  0 if 25 <= age <= 35
            - -2 if age > 35
            
        Args:
            boxer (Boxer): The boxer to calculate the skills

        Returns:
            float: The calculated fighting skill value.
        """
        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier

        return skill
