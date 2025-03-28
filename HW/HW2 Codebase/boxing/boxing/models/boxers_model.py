from dataclasses import dataclass
import logging
import sqlite3
from typing import Any, List

from boxing.utils.sql_utils import get_db_connection
from boxing.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Boxer:
    """
    A class to manage a boxer and their details / stats.

    Attributes:
        id (int): The current boxer.
                                    boxer id number starts at 1
        name (str): The name of the boxer.
        weight (int): The weight of the boxer,
                                    must be greater than 125.
        height (int): The height of the boxer.
                                    must be greater than 0.
        reach (float): Reach is the distance from the boxer's shoulder to their fist.
                                    must be greater than 0.
        age (int): The age of the boxer.
                                    must be between age of 18 and 40
        weight_class (str): the weight class of the boxer
                                    must be greater than 125 weight for weight class
                                    heavyweight - greater than or equal to weight of 203
                                    middleweight - between 166 and 203
                                    lightweight - between 133 and 166
                                    featherweight - between 125 and 133
    """
    id: int
    name: str
    weight: int
    height: int
    reach: float
    age: int
    weight_class: str = None

    def __post_init__(self):
        logger.info("Weight class for the boxer has been assigned")
        self.weight_class = get_weight_class(self.weight)  # Automatically assign weight class
        """Automatically assigns a weight class given the weight attribute.

        """

def create_boxer(name: str, weight: int, height: int, reach: float, age: int) -> None:
    """creates a new boxer to put in database.

    Args:
        name (str): The name of the new boxer.
        weight (int): The weight of the new boxer,
                                    must be greater than 125.
        height (int): The height of the new boxer.
                                    must be greater than 0.
        reach (float): Reach is the distance from the boxer's shoulder to their fist.
                                    must be greater than 0.
        age (int): The age of the new boxer.
                                    must be between age of 18 and 40

    Raises:
        ValueError: If the weight is below 125.
        ValueError: If the height is less than 0.
        ValueError: If the reach is less than 0.
        ValueError: If the age is not between 18 and 40.
        ValueError: If a boxer with the name already exists.
        e: catches any various database issues with sqlite3 during interaction and raises the exception e.

    """
    logger.info("Received request to add a new boxer to the database")
    if weight < 125:
        logger.error(f"Invalid weight: {weight}. Must be at least 125.")
        raise ValueError(f"Invalid weight: {weight}. Must be at least 125.")
    if height <= 0:
        logger.error(f"Invalid height: {height}. Must be greater than 0.")
        raise ValueError(f"Invalid height: {height}. Must be greater than 0.")
    if reach <= 0:
        logger.error(f"Invalid height: {height}. Must be greater than 0.")
        raise ValueError(f"Invalid reach: {reach}. Must be greater than 0.")
    if not (18 <= age <= 40):
        logger.error(f"Invalid age: {age}. Must be between 18 and 40.")
        raise ValueError(f"Invalid age: {age}. Must be between 18 and 40.")

    try:
        logger.info("Received request to access the database and add boxer")
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if the boxer already exists (name must be unique)
            cursor.execute("SELECT 1 FROM boxers WHERE name = ?", (name,))
            if cursor.fetchone():
                logger.error(f"Boxer with name '{name}' already exists")
                raise ValueError(f"Boxer with name '{name}' already exists")

            cursor.execute("""
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, height, reach, age))

            conn.commit()
            logger.info("boxer has succesfuly been added to the database")

    except sqlite3.IntegrityError:
        logger.error(f"Boxer with name '{name}' already exists")
        raise ValueError(f"Boxer with name '{name}' already exists")

    except sqlite3.Error as e:
        logger.error("a problem occured when interacting with the database")
        raise e


def delete_boxer(boxer_id: int) -> None:
    """deletes a certain boxer from the database.

    Args:
        boxer_id (int): The id of the boxer to remove.

    Raises:
        e: catches any various database issues with sqlite3 during interaction and raises the exception e.

    """
    logger.info("Received request to delete a boxer from the database")
    try:
        logger.info("Received request to access the database and delete boxer")
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.warning(f"Boxer with ID {boxer_id} was not found in the database.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()
            logger.info("Succesefuly removed boxer from the database")

    except sqlite3.Error as e:
        logger.error("a problem occured when interacting with the database")
        raise e


def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]:
    """access the leaderboard which is a list of boxers in a certain order specificed by sort_by

    Args:
        sort_by (str): the sorting type for the leaderboard of boxers
                                default value is wins if none is provided
        
    Returns:
        List[boxer]: A list of all boxers sorted in the way provided by sort_by
    Raises:
        ValueError: If the sort_by value is neither win_pct or wins
        
        e: catches any various database issues with sqlite3 during interaction and raises the exception e.

    """
    logger.info("Received request to access the leaderboard in order specificed by sort_by")
    query = """
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
    """

    if sort_by == "win_pct":
        query += " ORDER BY win_pct DESC"
        logger.info(f"Sorting the leaderboard by {sort_by}")
    elif sort_by == "wins":
        query += " ORDER BY wins DESC"
        logger.info(f"Sorting the leaderboard by {sort_by}")
    else:
        logger.error(f"Invalid sort_by parameter: {sort_by}")
        raise ValueError(f"Invalid sort_by parameter: {sort_by}")

    try:
        logger.info("Received request to access the database in order to create the leaderboard")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        leaderboard = []
        for row in rows:
            boxer = {
                'id': row[0],
                'name': row[1],
                'weight': row[2],
                'height': row[3],
                'reach': row[4],
                'age': row[5],
                'weight_class': get_weight_class(row[2]),  # Calculate weight class
                'fights': row[6],
                'wins': row[7],
                'win_pct': round(row[8] * 100, 1)  # Convert to percentage
            }
            leaderboard.append(boxer)
            logger.info(f"{boxer} has been added to the leaderboard")
        
        logger.info("The leaderboard has been succesfuly created")
        return leaderboard

    except sqlite3.Error as e:
        logger.error("a problem occured when interacting with the database")
        raise e


def get_boxer_by_id(boxer_id: int) -> Boxer:
    """creates a new boxer to put in database.

    Args:
        boxer_id (int): The id of the boxer object you want to get.
        
    Returns:
        boxer: returns a boxer object corresponding to the boxer_id
    Raises:
        ValueError: If no boxer was found with the given id
        e: catches any various database issues with sqlite3 during interaction and raises the exception e.

    """
    try:
        logger.info("Received request to access the database in order to get the boxer object given the id")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE id = ?
            """, (boxer_id,))

            row = cursor.fetchone()
            if row:
                logger.info("The boxer has been found in the database")
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                logger.info("The boxer has been succesfuly found and returned")
                return boxer
            else:
                logger.warning(f"Boxer with ID {boxer_id} not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")
            
    except sqlite3.Error as e:
        logger.error("a problem occured when interacting with the database")
        raise e


def get_boxer_by_name(boxer_name: str) -> Boxer:
    """
    Retrives a boxer from the database by their name.

    Args:
        boxer_name (str): The name of the boxer to retrieve.

    Returns:
        Boxer: A boxer object representing the retrieved boxer.
    
        Raises:
            ValueError: If no boxer was found with the given name
            sqlite3.Error: e exerception, any error occurred with the sqlite3 database
    """
    logger.info(f"Received request to fetch boxer by name: {boxer_name}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE name = ?
            """, (boxer_name,))

            row = cursor.fetchone()

            if row:
                logger.info(f"Boxer {boxer_name} found in the database." )
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                return boxer
            else:
                logger.warning(f"Boxer {boxer_name} not found")
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error while retrieving boxer by name {boxer_name}: {e}")
        raise e


def get_weight_class(weight: int) -> str:
    """
    Determines a boxer's weight class based on their weight.

    Args: 
        weight (int): The weight of the boxer.

    Returns:
        str: The weight class ('HEAVYWEIGHT', 'MIDDLEWEIGHT', 'LIGHTWEIGHT', or 'FEATHERWEIGHT').

    Raises: 
        ValueError: If weight is below 125, which is the minimum threshold
    """
    logger.info(f"Getting boxer's weight class based on their weight: {weight}")
    if weight >= 203:
        weight_class = 'HEAVYWEIGHT'
    elif weight >= 166:
        weight_class = 'MIDDLEWEIGHT'
    elif weight >= 133:
        weight_class = 'LIGHTWEIGHT'
    elif weight >= 125:
        weight_class = 'FEATHERWEIGHT'
    else:
        logger.error(f"Invalid weight: {weight}. Cannot assign weight class.")
        raise ValueError(f"Invalid weight: {weight}. Weight must be at least 125.")

    logger.info(f"Assigned weight class: {weight_class}")
    return weight_class


def update_boxer_stats(boxer_id: int, result: str) -> None:
    """
    Updates a boxer's record based on a match's result

    Increments the number of fights and, if the result is 'win', also increments wins.

    Args:
        boxer_id (int): The ID of the boxer whose record is to update
        result (str): The match's result ('win' or 'loss').
    
    Raises:
        ValueError: If the result is not 'win' or 'loss'.
        ValuError: If the boxer with the given ID was not found.
        sqlite3.Error: e exerception, any error occurred with the sqlite3 database
    """

    logger.info("Received request to update boxer {boxer_id} with result {result}.")

    if result not in {'win', 'loss'}:
        logger.error(f"Invalid result provided: {result}")
        raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info(f"Accessing database to update boxer with ID: {boxer_id}")

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.warning(f"Boxer with ID {boxer_id} not found in database.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            if result == 'win':
                logger.info("Updating boxer stats with a win.")
                cursor.execute("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (boxer_id,))
            else:  # result == 'loss'
                logger.info("Updating boxer stats with a loss.")
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))

            conn.commit()
            logger.info(f"Successfully updated stata for boxer with ID: {boxer_id}")

    except sqlite3.Error as e:
        logger.error(f"Database error while updating boxer stats: {e}")
        raise e
