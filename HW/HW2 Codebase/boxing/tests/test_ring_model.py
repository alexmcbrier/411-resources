import pytest

from boxing.models.ring_model import RingModel
from boxing.models.ring_model import Boxer


@pytest.fixture()
def ring_model():
    return RingModel()

@pytest.fixture
def mock_update_fight_record(mocker):
    return mocker.patch("boxing.models.ring_model.update_boxer_stats")

@pytest.fixture
def sample_boxer1():
    return Boxer(1, "Ali", 200, 180, 75.0, 30)
@pytest.fixture
def sample_boxer2():
    return Boxer(2, "Tyson", 230, 185, 80.0, 35)

@pytest.fixture
def sample_ring(sample_boxer1, sample_boxer2):
    return [sample_boxer1, sample_boxer2]

##################################################
# Boxer Management Tests
##################################################

def test_add_boxer_to_ring(ring_model, sample_boxer1):
    """Test adding a new boxer to the ring."""
    ring_model.enter_ring(sample_boxer1)
    assert len(ring_model.ring) == 1
    assert ring_model.ring[0].name == 'Ali'

def test_add_boxer_to_full_ring(ring_model, sample_boxer1, sample_boxer2):
    """Test adding a boxer to a full ring."""
    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)
    with pytest.raises(ValueError, match="Ring is full, cannot add more boxers."):
        ring_model.enter_ring(sample_boxer1)


def test_clear_ring(ring_model, sample_boxer1):
    """Test clearing the ring."""
    ring_model.enter_ring(sample_boxer1)
    assert len(ring_model.get_boxers()) == 1
    ring_model.clear_ring()
    assert len(ring_model.get_boxers()) == 0

##################################################
# Fight Management Tests
##################################################
def test_fight(ring_model, sample_boxer1, sample_boxer2, mock_update_fight_record):
    """Test fight simulation between two boxers."""
    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)

    winner_name = ring_model.fight()
    
    winner = sample_boxer1 if winner_name == sample_boxer1.name else sample_boxer2
    loser = sample_boxer2 if winner == sample_boxer1 else sample_boxer1

    assert winner_name in [sample_boxer1.name, sample_boxer2.name]
    mock_update_fight_record.assert_any_call(winner.id, 'win')
    mock_update_fight_record.assert_any_call(loser.id, 'loss')



def test_fight_not_enough_boxers(ring_model, sample_boxer1):
    """Test that a fight is not possible with less than 2 boxers."""
    ring_model.enter_ring(sample_boxer1)
    with pytest.raises(ValueError, match="There must be two boxers to start a fight."):
        ring_model.fight()

def test_fight_winner_stats_update(ring_model, sample_boxer1, sample_boxer2, mock_update_fight_record):
    """Test that the winner's stats are updated correctly after a fight."""
    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)

    winner_name = ring_model.fight()

    winner = sample_boxer1 if sample_boxer1.name == winner_name else sample_boxer2
    loser = sample_boxer2 if winner == sample_boxer1 else sample_boxer1

    mock_update_fight_record.assert_any_call(winner.id, 'win')
    mock_update_fight_record.assert_any_call(loser.id, 'loss')


##################################################
# Boxer Skill Calculation Tests
##################################################
def test_get_fighting_skill(ring_model, sample_boxer1):
    """Test calculating the fighting skill of a boxer."""
    skill = ring_model.get_fighting_skill(sample_boxer1)
    assert skill == (sample_boxer1.weight * len(sample_boxer1.name)) + (sample_boxer1.reach / 10)


def test_get_fighting_skill_with_age(ring_model, sample_boxer2):
    """Test calculating the fighting skill with age modifier."""
    sample_boxer2.age = 40 #age changes skill so add it in to make sure its correct
    skill = ring_model.get_fighting_skill(sample_boxer2)
    assert skill == (sample_boxer2.weight * len(sample_boxer2.name)) + (sample_boxer2.reach / 10) -2


def test_get_fighting_skill_with_name(ring_model, sample_boxer2):
    """Test calculating the fighting skill considering name length."""
    sample_boxer2.name = "BoxerX"  #name changes skill so add it in to make sure its correct
    skill = ring_model.get_fighting_skill(sample_boxer2)
    assert skill == (sample_boxer2.weight * len(sample_boxer2.name)) + (sample_boxer2.reach / 10) 

##################################################
# Ring State Tests
##################################################
def test_get_boxers(ring_model, sample_boxer1, sample_boxer2):
    """Test retrieving all boxers in the ring."""
    ring_model.enter_ring(sample_boxer1)
    ring_model.enter_ring(sample_boxer2)
    boxers = ring_model.get_boxers()
    assert len(boxers) == 2
    assert sample_boxer1 in boxers
    assert sample_boxer2 in boxers