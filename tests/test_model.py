import time

import pytest

from crazy_clicker_game import CrazyClickerModel


@pytest.fixture
def model():
    return CrazyClickerModel(
        start_phrase='start',
        gaming_phrases=['one', 'two', 'three'],
        fail_phrase='fail',
        win_phrase='win',
    )


def test__register_click__click_increments(model):
    model.start_game(clicks=1, seconds=1)
    assert model.clicks == 0
    model.register_click()
    assert model.clicks == 1


def test__state__state_before_start(model):
    assert model.state is None


def test__state__gaming(model):
    model.start_game(clicks=2, seconds=1)
    assert model.state == 'game'
    model.register_click()
    assert model.state == 'game'


def test__state__fail(model):
    model.start_game(clicks=1, seconds=0.1)
    time.sleep(0.2)
    assert model.phrase == 'fail'


def test__state__win(model):
    model.start_game(clicks=1, seconds=1)
    model.register_click()
    assert model.state == 'win'


def test__phrase__before_start(model):
    assert model.phrase == 'start'


def test__phrase__gaming(model):
    model.start_game(clicks=3, seconds=1)
    assert model.phrase == 'one'
    model.register_click()
    assert model.phrase == 'two'
    model.register_click()
    assert model.phrase == 'three'
    model.register_click()
    assert model.phrase == 'win'


def test__phrase__fail(model):
    model.start_game(clicks=1, seconds=0.1)
    time.sleep(0.2)
    assert model.state == 'fail'


def test__phrase__win(model):
    model.start_game(clicks=1, seconds=1)
    model.register_click()
    assert model.phrase == 'win'


def test__seconds_left(model):
    model.start_game(clicks=1, seconds=2)
    time.sleep(1)
    assert 0 < model.seconds_left < 2
