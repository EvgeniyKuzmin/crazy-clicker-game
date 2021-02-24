from crazy_clicker_game import CrazyClickerModel


def test__register_click__click_increments():
    model = CrazyClickerModel()
    model.start_game(1, 1)
    assert model.clicks == 0
    model.register_click()
    assert model.clicks == 1


def test__state__state_before_start():
    model = CrazyClickerModel()
    assert model.state is None
