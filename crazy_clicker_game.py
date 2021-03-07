from collections import Counter
from itertools import chain, repeat
from random import randint
import time
import tkinter as tk
from tkinter import messagebox
from typing import Any, Dict, Optional, Sequence


CONFIG = {
    'view_settings': {
        'title': 'CRAZY CLICKER',
        'window_size': {
            'width': 410,
            'height': 170,
        },
        'seconds': {
            'default': 10,
            'min': 10,
            'max': 120,
        },
        'clicks': {
            'default': 50,
            'min': 10,
            'max': 300,
        },
        'button': {
            'width': 191,
            'height': 47,
        },
        'colors': {
            'menu': 'grey',
            'surface': 'white',
        },
        'fonts': {
            'L': ('Arial', '18'),
            'S': ('Arial', '14'),
        },
    },
    'phrases': {
        'start_phrase': 'Click START',
        'win_phrase': 'Well done...',
        'fail_phrase': 'Game Over',
        'gaming_phrases': [
            'Click me',
            'Faster!',
            'MUCH FASTER!',
            'PUSH, PUSH!!',
            'Give MORE!',
            'Almost...',
        ],
    },
}


class CrazyClickerModel:

    _states = ('game', 'win', 'fail')

    def __init__(
            self, start_phrase: str, gaming_phrases: Sequence[str],
            fail_phrase: str, win_phrase: str) -> None:

        self._start_phrase = start_phrase
        self._gaming_phrases = gaming_phrases
        self._fail_phrase = fail_phrase
        self._win_phrase = win_phrase

        self.clicks = None
        self._clicks_to_win = None
        self._start_time = None
        self._end_time = None
        self._phrase_mapping = None

    def start_game(self, clicks: int, seconds: int) -> None:
        self.clicks = 0
        self._clicks_to_win = clicks
        self._start_time = time.time()
        self._end_time = self._start_time + seconds
        self._phrase_mapping = {
            click_index: phrase for click_index, phrase in enumerate(
                chain.from_iterable(
                    repeat(phr, cnt) for phr, cnt in
                    Counter(
                        self._gaming_phrases[ci % len(self._gaming_phrases)]
                        for ci in range(self._clicks_to_win)
                    ).items()))
        }

    def register_click(self) -> None:
        self.clicks += 1

    @property
    def seconds_left(self) -> int:
        return int(time.time() - self._start_time)

    @property
    def state(self) -> Optional[str]:
        if self.clicks is None:
            return None
        if self.clicks >= self._clicks_to_win:
            return self._states[1]  # win
        elif self._end_time - time.time() > 0:
            return self._states[0]  # game
        else:
            return self._states[2]  # fail

    @property
    def phrase(self) -> str:
        if self.state is None:
            return self._start_phrase
        elif self.state == 'win':
            return self._win_phrase
        elif self.state == 'fail':
            return self._fail_phrase
        else:
            return self._phrase_mapping[self.clicks]


class CrazyClickerController:

    def __init__(self, model: 'CrazyClickerModel') -> None:
        self._model = model
        self._view = None

    def set_view(self, view: 'CrazyClickerInterface') -> None:
        self._view = view

    def start_game(self) -> None:
        self._model.start_game(self._view.press_count, self._view.time)
        self._view.draw_initial_state(self._model.phrase)
        self.update_time()

    def update_time(self) -> None:
        if self._model.state == 'game':
            self._view.update_time_label(self._model.seconds_left)
            self._view.after(1000, self.update_time)
        elif self._model.state == 'fail':
            self._view.draw_end_game(win=False, phrase=self._model.phrase)

    def update_count(self) -> None:
        if self._view.mode:
            self._view.move_button()

        self._model.register_click()
        if self._model.state == 'game':
            self._view.update_button_phrase(self._model.phrase)
            self._view.update_click_label(self._model.clicks)
        else:
            self._view.draw_end_game(
                win=self._model.state == 'win',
                phrase=self._model.phrase)

    def run_application(self) -> None:
        self._view.build(self._model.phrase)
        self._view.master.mainloop()


class CrazyClickerInterface(tk.Frame):

    def __init__(
            self, controller: 'CrazyClickerController',
            settings: Dict[str, Any]) -> None:

        self._controller = controller
        self._settings = settings

        self.master = None
        self._build_master()

        self._mode_var = tk.BooleanVar()
        self._time_var = tk.IntVar()
        self._press_count_var = tk.IntVar()
        self.time = self._settings['seconds']['default']
        self.press_count = self._settings['clicks']['default']

        self._start_game_button = None
        self._buttons_frame = None
        self._button = None
        self._time_last_label = None
        self._click_count_label = None

    def _build_master(self) -> None:
        root = tk.Tk()
        root.title(self._settings['title'])
        root.minsize(**self._settings['window_size'])
        self.master = root
        super().__init__(self.master)

    def _build_menu_frame(self) -> None:
        frame_menu = tk.Frame(self, bg=self._settings['colors']['menu'])
        frame_menu.pack(side='top', fill='x')

        frame_menu_fields = tk.Frame(
            frame_menu, bg=self._settings['colors']['menu'])
        frame_menu_fields.pack(padx=5, pady=5)

        mode_check = tk.Checkbutton(
            frame_menu_fields,
            variable=self._mode_var,
            font=self._settings['fonts']['S'],
            bg=self._settings['colors']['menu'])
        mode_check.pack(side='left')

        time_set_lab = tk.Label(
            frame_menu_fields,
            text='Time:', font=self._settings['fonts']['S'],
            bg=self._settings['colors']['menu'])
        time_set_lab.pack(side='left')

        time_spin = tk.Spinbox(
            frame_menu_fields,
            width=3,
            from_=self._settings['seconds']['min'],
            to=self._settings['seconds']['max'],
            textvariable=self._time_var,
            font=self._settings['fonts']['L'])
        time_spin.pack(side='left', fill='y')

        count_set_lab = tk.Label(
            frame_menu_fields,
            text='Clicks:',
            font=self._settings['fonts']['S'],
            bg=self._settings['colors']['menu'])
        count_set_lab.pack(side='left')

        press_count_spin = tk.Spinbox(
            frame_menu_fields,
            width=3,
            from_=self._settings['clicks']['min'],
            to=self._settings['clicks']['max'],
            textvariable=self._press_count_var,
            font=self._settings['fonts']['L'])
        press_count_spin.pack(side='left', fill='y')

        self._start_game_button = tk.Button(
            frame_menu_fields,
            text='START',
            font=self._settings['fonts']['S'],
            command=self._controller.start_game)
        self._start_game_button.pack(side='left', padx=5)

    def _build_game_frame(self, phrase: str) -> None:
        frame_game = tk.Frame(self)
        frame_game.pack(fill='both', expand=True)

        self._buttons_frame = tk.Frame(frame_game)
        self._buttons_frame.pack(fill='both', expand=True, padx=15, pady=15)

        self._button = tk.Button(
            self._buttons_frame,
            text=phrase,
            width=13,
            font=self._settings['fonts']['L'])
        self._button.config(
            command=self._controller.update_count, state='disabled')
        self._button.pack(expand=True)

    def _build_result_frame(self) -> None:
        frame_result = tk.Frame(self, bg=self._settings['colors']['surface'])
        frame_result.pack(side='bottom', fill='x')

        frame_result_fields = tk.Frame(frame_result)
        frame_result_fields.pack(padx=5, pady=5)

        self._time_last_label = tk.Label(
            frame_result_fields,
            text='Time: 000 сек.', bg=self._settings['colors']['surface'],
            font=self._settings['fonts']['S'])
        self._time_last_label.pack(side='left')

        self._click_count_label = tk.Label(
            frame_result_fields,
            text='Clicks: 000', bg=self._settings['colors']['surface'],
            font=self._settings['fonts']['S'])
        self._click_count_label.pack(side='left')

    def build(self, start_phrase: str) -> None:
        self.pack(fill='both', expand=True)
        self._build_menu_frame()
        self._build_game_frame(start_phrase)
        self._build_result_frame()

    def move_button(self, to_center: bool = False) -> None:
        max_width = (
            self._buttons_frame.winfo_width()
            - self._settings['button']['width']
        )
        max_height = (
            self._buttons_frame.winfo_height()
            - self._settings['button']['height']
        )
        self._button.place_forget()
        self._button.place(
            x=max_width // 2 if to_center else randint(0, max_width),
            y=max_height // 2 if to_center else randint(0, max_height),
            width=self._settings['button']['width'],
            height=self._settings['button']['height'])

    @property
    def mode(self) -> bool:
        return self._mode_var.get()

    @property
    def press_count(self) -> int:
        return self._press_count_var.get()

    @press_count.setter
    def press_count(self, value: int) -> None:
        self._press_count_var.set(value)

    @property
    def time(self) -> int:
        return self._time_var.get()

    @time.setter
    def time(self, value: int) -> None:
        self._time_var.set(value)

    def update_time_label(self, seconds: int) -> None:
        self._time_last_label.config(text=f'Time: {seconds % 1000:03} sec.')

    def update_click_label(self, clicks: int) -> None:
        self._click_count_label.config(text=f'Clicks: {clicks:03}')

    def update_button_phrase(self, phrase: str) -> None:
        self._button.config(text=phrase)

    def draw_initial_state(self, phrase: str) -> None:
        self._time_last_label.config(text='Time: 000 сек.')
        self._click_count_label.config(text='Clicks: 000')
        self._button.config(state='normal', text=phrase)
        if self.mode:
            self.move_button(to_center=True)
        else:
            self._button.pack(expand=True)

    def draw_end_game(self, win: bool, phrase: str) -> None:
        self._button.config(state='disabled', text=phrase)
        if win:
            messagebox.showinfo('Game over', 'You win!')
        else:
            messagebox.showinfo('Game over', 'You lose!')


def main() -> None:
    model = CrazyClickerModel(**CONFIG['phrases'])
    controller = CrazyClickerController(model)
    view = CrazyClickerInterface(controller, CONFIG['view_settings'])

    controller.set_view(view)
    controller.run_application()


if __name__ == '__main__':
    main()
