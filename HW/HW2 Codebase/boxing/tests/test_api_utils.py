import pytest
import requests

from boxing.utils.api_utils import get_random

RANDOM_FLOAT = 0.73


@pytest.fixture
def mock_random_org(mocker):
    """Mock the response from requests.get to return a valid float string."""
    mock_response = mocker.Mock()
    mock_response.text = f"{RANDOM_FLOAT}"
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response


def test_get_random_success(mock_random_org):
    """Test retrieving a random float from random.org."""
    result = get_random()

    # Assert that the result is the mocked random float
    assert result == RANDOM_FLOAT, f"Expected {RANDOM_FLOAT}, but got {result}"

    # Ensure that the correct URL was called
    requests.get.assert_called_once_with(
        "https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new",
        timeout=5
    )


def test_get_random_timeout(mocker):
    """Test handling of a timeout when calling random.org."""
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)

    with pytest.raises(RuntimeError, match="Request to random.org timed out."):
        get_random()


def test_get_random_request_failure(mocker):
    """Test handling of a general request failure."""
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("Boom"))

    with pytest.raises(RuntimeError, match="Request to random.org failed: Boom"):
        get_random()


def test_get_random_invalid_response(mock_random_org):
    """Test handling of an invalid (non-float) response."""
    mock_random_org.text = "not_a_float"

    with pytest.raises(ValueError, match="Invalid response from random.org: not_a_float"):
        get_random()
