import re
import sqlite3
from contextlib import contextmanager

import pytest

from boxing.models.boxers_model import (
    Boxer,
    create_boxer,
    delete_boxer,
    get_boxer_by_id,
    get_boxer_by_name,
    get_leaderboard,
    update_boxer_stats,
    get_weight_class
)

######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn # Yield the mocked connection object

    mocker.patch("boxing.models.boxers_model.get_db_connection", mock_get_db_connection)

    return mock_cursor # Return the mock cursor so we can set expectations per test

######################################################
#
#    Add and delete
#
######################################################

def test_create_boxer(mock_cursor):
    """ Test creating a new boxer

    """
    create_boxer("Ali", 200, 180, 75.0, 30)

    expected_query = normalize_whitespace("""
        INSERT INTO boxers (name, weight, height, reach, age)
        VALUES (?, ?, ?, ?, ?)
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    expected_arguments = ("Ali", 200, 180, 75.0, 30)
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_boxer_duplicate(mock_cursor):
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed")
    with pytest.raises(ValueError, match="Boxer with name 'Ali' already exists"):
        create_boxer("Ali", 200, 180, 75.0, 30)

def test_create_boxer_invalid_weight():
    """Test error when creating a boxer with invalid weight (below 125)."""
    with pytest.raises(ValueError, match=r"Invalid weight: 120. Must be at least 125."):
        create_boxer("Ali", 120, 180, 70.0, 25)


def test_create_boxer_invalid_height():
    """Test error when creating a boxer with invalid height (zero or negative)."""
    with pytest.raises(ValueError, match=r"Invalid height: 0. Must be greater than 0."):
        create_boxer("Tyson", 130, 0, 72.0, 30)

    with pytest.raises(ValueError, match=r"Invalid height: -10. Must be greater than 0."):
        create_boxer("Tyson", 130, -10, 72.0, 30)

def test_create_boxer_invalid_reach():
    """Test error when creating a boxer with invalid reach (zero or negative)."""
    with pytest.raises(ValueError, match=r"Invalid reach: 0. Must be greater than 0."):
        create_boxer("Gabriel", 135, 180, 0, 28)

    with pytest.raises(ValueError, match=r"Invalid reach: -5. Must be greater than 0."):
        create_boxer("Gabriel", 135, 180, -5, 28)

def test_create_boxer_invalid_age():
    """Test error when creating a boxer with invalid age (outside 18-40)."""
    with pytest.raises(ValueError, match=r"Invalid age: 17. Must be between 18 and 40."):
        create_boxer("Levi", 140, 180, 72.0, 17)

    with pytest.raises(ValueError, match=r"Invalid age: 41. Must be between 18 and 40."):
        create_boxer("Levi", 140, 180, 72.0, 41)

def test_delete_boxer(mock_cursor):
    """Test deleting a boxer from the database by boxer ID.
    """
    # Simulate that the boxer with ID 1 exists
    mock_cursor.fetchone.return_value = True

    delete_boxer(1)

    expected_select_sql = normalize_whitespace("SELECT id FROM boxers WHERE id = ?")
    expected_delete_sql = normalize_whitespace("DELETE FROM boxers WHERE id = ?")

    # Get both SQL queries executed
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_delete_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_select_sql == expected_select_sql, "The SELECT SQL query did not match the expected structure."
    assert actual_delete_sql == expected_delete_sql, "The DELETE SQL query did not match the expected structure."

    expected_select_args = (1,)
    expected_delete_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_delete_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT SQL query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_delete_args == expected_delete_args, f"The DELETE SQL query arguments did not match. Expected {expected_delete_args}, got {actual_delete_args}."


######################################################
#
#    Get Boxer
#
######################################################

def test_get_boxer_by_id(mock_cursor):
    """Test getting a boxer by id."""
    mock_cursor.fetchone.return_value = (1, "Ali", 200, 180, 75.0, 30)

    result = get_boxer_by_id(1)

    expected_result = Boxer(1, "Ali", 200, 180, 75.0, 30)

    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_query = normalize_whitespace("SELECT id, name, weight, height, reach, age FROM boxers WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    expected_arguments = (1,)
    actual_arguments = mock_cursor.execute.call_args[0][1]
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_get_boxer_by_id_bad_id(mock_cursor):
    """Test error when getting a non-existent boxer."""
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer with ID 999 not found."):
        get_boxer_by_id(999)

def test_get_boxer_by_name(mock_cursor):
    """Test getting a boxer by name."""
    mock_cursor.fetchone.return_value = (1, "Ali", 200, 180, 75.0, 30)

    result = get_boxer_by_name("Ali")

    expected_result = Boxer(1, "Ali", 200, 180, 75.0, 30)

    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_query = normalize_whitespace("SELECT id, name, weight, height, reach, age FROM boxers WHERE name = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    expected_arguments = ("Ali",)
    actual_arguments = mock_cursor.execute.call_args[0][1]
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_get_boxer_by_name_not_found(mock_cursor):
    """Test error when boxer name is not found."""
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer 'Ali' not found."):
        get_boxer_by_name("Ali")

######################################################
#
#    Get Leaderboard
#
######################################################

def test_get_leaderboard_ordered_by_wins(mock_cursor):
    """Test retrieving the leaderboard ordered by number of wins."""
    mock_cursor.fetchall.return_value = [
    (2, "Tyson", 230, 185, 80.0, 35, 12, 10, 0.83),
    (1, "Ali", 200, 180, 75.0, 30, 10, 8, 0.8),  
    (3, "George", 210, 190, 78.0, 32, 8, 6, 0.75)
]
    result = get_leaderboard(sort_by="wins")
    
    expected_result = [
    {'id': 2, 'name': 'Tyson', 'weight': 230, 'height': 185, 'reach': 80.0, 'age': 35, 'weight_class': 'HEAVYWEIGHT', 'fights': 12, 'wins': 10, 'win_pct': 83.0}, 
    {'id': 1, 'name': 'Ali', 'weight': 200, 'height': 180, 'reach': 75.0, 'age': 30, 'weight_class': 'MIDDLEWEIGHT', 'fights': 10, 'wins': 8, 'win_pct': 80.0}, 
    {'id': 3, 'name': 'George', 'weight': 210, 'height': 190, 'reach': 78.0, 'age': 32, 'weight_class': 'HEAVYWEIGHT', 'fights': 8, 'wins': 6, 'win_pct': 75.0}
    ]
    
    # Assert that the leaderboard matches the expected result
    assert result == expected_result, f"Expected {expected_result}, but got {result}"

    expected_query = normalize_whitespace("""
        SELECT id, name, weight, height, reach, age, fights, wins, (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
        ORDER BY wins DESC           
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."
    # mock fetchall to return multiple rows,
    # and assert that the results are sorted by the 'wins' field.

def test_get_leaderboard_ordered_by_win_pct(mock_cursor):
    """Test retrieving the leaderboard ordered by win percentage."""
    mock_cursor.fetchall.return_value = [
    (2, "Tyson", 230, 185, 80.0, 35, 12, 10, 0.83),
    (1, "Ali", 200, 180, 75.0, 30, 10, 8, 0.8),  
    (3, "George", 210, 190, 78.0, 32, 8, 6, 0.75)
]
    result = get_leaderboard(sort_by="wins")
    
    expected_result = [
    {'id': 2, 'name': 'Tyson', 'weight': 230, 'height': 185, 'reach': 80.0, 'age': 35, 'weight_class': 'HEAVYWEIGHT', 'fights': 12, 'wins': 10, 'win_pct': 83.0}, 
    {'id': 1, 'name': 'Ali', 'weight': 200, 'height': 180, 'reach': 75.0, 'age': 30, 'weight_class': 'MIDDLEWEIGHT', 'fights': 10, 'wins': 8, 'win_pct': 80.0}, 
    {'id': 3, 'name': 'George', 'weight': 210, 'height': 190, 'reach': 78.0, 'age': 32, 'weight_class': 'HEAVYWEIGHT', 'fights': 8, 'wins': 6, 'win_pct': 75.0}
    ]
    
    # Assert that the leaderboard matches the expected result
    assert result == expected_result, f"Expected {expected_result}, but got {result}"

    expected_query = normalize_whitespace("""
        SELECT id, name, weight, height, reach, age, fights, wins, (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
        ORDER BY wins DESC           
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."
    # validate that win_pct is calculated correctly
    # and ordering is based on that column.

def test_get_leaderboard_invalid_sort_by(mock_cursor):
    """Test error when sort_by parameter is invalid (e.g., 'losses')."""
    # Provide an invalid string and assert that ValueError is raised.
    mock_cursor.fetchone.return_value = None
    invalid_sort_by = 'losses'
    with pytest.raises(ValueError, match="Invalid sort_by parameter: losses"):
        get_leaderboard(sort_by=invalid_sort_by)

######################################################
#
#    Get Weight Class
#
######################################################
def test_get_weight_class_heavyweight():
    """Test weight class assignment: HEAVYWEIGHT (>= 203)."""
    assert get_weight_class(250) == "HEAVYWEIGHT"
    assert get_weight_class(203) == "HEAVYWEIGHT"


def test_get_weight_class_middleweight():
    """Test weight class assignment: MIDDLEWEIGHT (166 <= weight < 203)."""
    assert get_weight_class(166) == "MIDDLEWEIGHT"
    assert get_weight_class(180) == "MIDDLEWEIGHT"
    assert get_weight_class(202) == "MIDDLEWEIGHT"


def test_get_weight_class_lightweight():
    """Test weight class assignment: LIGHTWEIGHT (133 <= weight < 166)."""
    assert get_weight_class(133) == "LIGHTWEIGHT"
    assert get_weight_class(150) == "LIGHTWEIGHT"
    assert get_weight_class(165) == "LIGHTWEIGHT"


def test_get_weight_class_featherweight():
    """Test weight class assignment: FEATHERWEIGHT (125 <= weight < 133)."""
    assert get_weight_class(125) == "FEATHERWEIGHT"
    assert get_weight_class(130) == "FEATHERWEIGHT"
    assert get_weight_class(132) == "FEATHERWEIGHT"


def test_get_weight_class_invalid():
    """Test error when weight is below the minimum threshold."""
    with pytest.raises(ValueError, match=r"Invalid weight: 120\. Weight must be at least 125\."):
        get_weight_class(120)
        
######################################################
#
#    Update Boxer
#
######################################################
def test_update_boxer_stats_win(mock_cursor):
    """Test updating boxer stats after a win (should increase both fights and wins)."""
    mock_cursor.fetchone.return_value = True
    
    boxer_id = 1 
    result = 'win' 
    update_boxer_stats(boxer_id, result)
    expected_query = normalize_whitespace("""
        UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    assert actual_query == expected_query, "The SQL query did not match the expected structure."
    
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    expected_arguments = (boxer_id,)
    
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."
    # Simulate SELECT returning a boxer and assert the UPDATE query is correct.
    

def test_update_boxer_stats_loss(mock_cursor):
    """Test updating boxer stats after a loss (should increase only fights)."""
    mock_cursor.fetchone.return_value = True
    
    boxer_id = 1 
    result = 'loss' 
    update_boxer_stats(boxer_id, result)
    expected_query = normalize_whitespace("""
        UPDATE boxers SET fights = fights + 1 WHERE id = ?
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    assert actual_query == expected_query, "The SQL query did not match the expected structure."
    
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    expected_arguments = (boxer_id,)
    
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."
    # Simulate SELECT returning a boxer and assert the UPDATE query for loss is correct.
    pass

def test_update_boxer_stats_invalid_result(mock_cursor):
    """Test error when result is not 'win' or 'loss'."""
    # Pass a result like 'draw' and ensure it raises a ValueError.
    mock_cursor.fetchone.return_value = None
    boxer_id = 1 
    invalid_result = 'draw' 
    with pytest.raises(ValueError, match="Invalid result: draw. Expected 'win' or 'loss'."):
        update_boxer_stats(boxer_id, invalid_result)



def test_update_boxer_stats_bad_id(mock_cursor):
    """Test error when updating stats for a non-existent boxer."""
    # Simulate SELECT returning None and ensure ValueError is raised.
    mock_cursor.fetchone.return_value = None
    invalid_id = 5 
    result = 'win' 
    with pytest.raises(ValueError, match="Boxer with ID 5 not found."):
        update_boxer_stats(invalid_id, result)