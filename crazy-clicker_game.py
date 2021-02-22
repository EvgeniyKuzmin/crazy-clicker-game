from itertools import chain, repeat
from random import randint
import time
import tkinter as tk
from tkinter import messagebox
from typing import Optional


CONFIG = {
    'title': 'CRAZY CLICKER',
    'defaults': {
        'seconds': 10,
        'seconds_min': 10,
        'seconds_max': 120,
        'clicks': 50,
        'clicks_min': 10,
        'clicks_max': 300,
        'button_width': 191,
        'button_height': 47,
    },
    'colors': {
        'menu': 'grey',
        'surface': 'white',
    },
    'fonts': {
        'L': ('Arial', '18'),
        'S': ('Arial', '14'),
    },
    'window_size': {
        'width': 410,
        'height': 170,
    },
}


class CrazyClickerModel:

    _phrases = (
        'Click me',
        'Faster!',
        'MUCH FASTER!',
        'PUSH, PUSH!!',
        'Give MORE!',
        'Almost...',
        'Well done...',
    )
    _states = ('game', 'win', 'fail')

    def __init__(self) -> None:
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
            i: self._phrases[phrase_i] for i, phrase_i in enumerate(chain(
                repeat(0, self._clicks_to_win % (len(self._phrases) - 1)),
                *[
                    repeat(i, self._clicks_to_win // (len(self._phrases) - 1))
                    for i in range(len(self._phrases))
                ]))
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
            return 'Click START'
        if self.state == 'win':
            return self._phrases[-1]
        elif self.state == 'fail':
            return 'Game Over'
        else:
            try:
                return self._phrase_mapping[self.clicks]
            except KeyError:
                return self._phrases[0]


class CrazyClickerInterface(tk.Frame):

    def __init__(
            self, master, seconds, seconds_min, seconds_max, clicks,
            clicks_min, clicks_max, button_width, button_height, model):

        self._model = model
        super().__init__(master)
        self.master = master

        self.button_width = button_width
        self.button_height = button_height
        self.seconds_min = seconds_min
        self.seconds_max = seconds_max
        self.clicks_min = clicks_min
        self.clicks_max = clicks_max

        self.mode_var = tk.BooleanVar()
        self.time_var = tk.IntVar()
        self.time_var.set(seconds)
        self.press_count_var = tk.IntVar()
        self.press_count_var.set(clicks)

        self.start_game_button = None
        self.frame_with_button = None
        self.button = None
        self.time_last_label = None
        self.click_count_label = None

        self.button_clicks = 0
        self.stop_game = False
        self.start_time = int(time.time())
        self.click_phrase_mapping = None

    def build(self):
        self.pack(fill='both', expand=True)
        self._build_menu_frame()
        self._build_game_frame()
        self._build_result_frame()

    def _build_menu_frame(self):
        frame_menu = tk.Frame(self, bg=CONFIG['colors']['menu'])
        frame_menu.pack(side='top', fill='x')

        frame_menu_fields = tk.Frame(frame_menu, bg=CONFIG['colors']['menu'])
        frame_menu_fields.pack(padx=5, pady=5)

        mode_check = tk.Checkbutton(
            frame_menu_fields,
            variable=self.mode_var, font=CONFIG['fonts']['S'],
            bg=CONFIG['colors']['menu'])
        mode_check.pack(side='left')

        time_set_lab = tk.Label(
            frame_menu_fields,
            text='Time:', font=CONFIG['fonts']['S'],
            bg=CONFIG['colors']['menu'])
        time_set_lab.pack(side='left')

        time_spin = tk.Spinbox(
            frame_menu_fields,
            width=3, from_=self.seconds_min, to=self.seconds_max,
            textvariable=self.time_var, font=CONFIG['fonts']['L'])
        time_spin.pack(side='left', fill='y')

        count_set_lab = tk.Label(
            frame_menu_fields,
            text='Clicks:', font=CONFIG['fonts']['S'],
            bg=CONFIG['colors']['menu'])
        count_set_lab.pack(side='left')

        press_count_spin = tk.Spinbox(
            frame_menu_fields,
            width=3, from_=self.clicks_min, to=self.clicks_max,
            textvariable=self.press_count_var, font=CONFIG['fonts']['L'])
        press_count_spin.pack(side='left', fill='y')

        self.start_game_button = tk.Button(
            frame_menu_fields,
            text='START', command=self.start_game, font=CONFIG['fonts']['S'])
        self.start_game_button.pack(side='left', padx=5)

    def _build_game_frame(self):
        frame_game = tk.Frame(self)
        frame_game.pack(fill='both', expand=True)

        self.frame_with_button = tk.Frame(frame_game)
        self.frame_with_button.pack(fill='both', expand=True, padx=15, pady=15)

        self.button = tk.Button(
            self.frame_with_button,
            text=self._model.phrase, width=13, font=CONFIG['fonts']['L'])
        self.button.config(command=self.update_count, state='disabled')
        self.button.pack(expand=True)

    def _build_result_frame(self):
        frame_result = tk.Frame(self, bg=CONFIG['colors']['surface'])
        frame_result.pack(side='bottom', fill='x')

        frame_result_fields = tk.Frame(frame_result)
        frame_result_fields.pack(padx=5, pady=5)

        self.time_last_label = tk.Label(
            frame_result_fields,
            text='Time: 000 сек.', bg=CONFIG['colors']['surface'],
            font=CONFIG['fonts']['S'])
        self.time_last_label.pack(side='left')

        self.click_count_label = tk.Label(
            frame_result_fields,
            text='Clicks: 000', bg=CONFIG['colors']['surface'],
            font=CONFIG['fonts']['S'])
        self.click_count_label.pack(side='left')

    def _move_button(self, to_center: bool = False) -> None:
        max_width = self.frame_with_button.winfo_width() - self.button_width
        max_height = self.frame_with_button.winfo_height() - self.button_height
        self.button.place_forget()
        self.button.place(
            x=max_width // 2 if to_center else randint(0, max_width),
            y=max_height // 2 if to_center else randint(0, max_height),
            width=self.button_width, height=self.button_height)

    def start_game(self):
        self._model.start_game(self.press_count_var.get(), self.time_var.get())
        self.time_last_label.config(text='Time: 000 сек.')
        self.click_count_label.config(text='Clicks: 000')
        self.button.config(state='normal', text=self._model.phrase)
        if self.mode_var.get():
            self._move_button(to_center=True)
        else:
            self.button.pack(expand=True)
        self.update_time()

    def update_count(self):
        if self.mode_var.get():
            self._move_button()

        self._model.register_click()
        if self._model.state == 'game':
            self.button.config(text=self._model.phrase)
            self.click_count_label.config(
                text=f'Clicks: {self._model.clicks:03}')
        else:
            self.button.config(state='disabled', text=self._model.phrase)
            if self._model.state == 'fail':
                messagebox.showinfo('Game over', 'You lose!')
            else:  # win
                messagebox.showinfo('Game over', 'You win!')

    def update_time(self):
        if self._model.state == 'game':
            self.time_last_label.config(
                text=f'Time: {self._model.seconds_left % 1000:03} sec.')
            self.after(1000, self.update_time)
        elif self._model.state == 'fail':
            messagebox.showinfo('Game over', 'You lose!')
            self.button.config(state='disabled', text=self._model.phrase)


def main():
    root = tk.Tk()
    root.title(CONFIG['title'])
    root.minsize(**CONFIG['window_size'])

    model = CrazyClickerModel()
    view = CrazyClickerInterface(root, **CONFIG['defaults'], model=model)
    view.build()
    root.mainloop()


if __name__ == '__main__':
    main()
