# Copyright (C) 2019 Valentin Vanelslande
# Licensed under GPLv2 or any later version
# Refer to the license.txt file included.

import time
from ctypes import windll

import pypresence
import win32gui

found_window = False
cv_closed = False
old_text = None


def parse_title(text):
    parts = text.split(' | ')
    if len(parts) == 0:
        return ('unknown version', None)
    elif len(parts) == 1:
        return (parts[0], None)
    elif len(parts) >= 2:
        return (parts[0], parts[1])


def enum_callback(hwnd, unknown):
    global cv_closed
    global old_text
    global found_window

    text = win32gui.GetWindowText(hwnd)

    if text.startswith('Citra Valentin '):
        found_window = True
        start = time.time()

        rpc = pypresence.Presence(633487273413050418)
        rpc.connect()

        print('Discord RPC: connected.')

        try:
            while True:
                if not windll.user32.IsWindow(hwnd):
                    break

                text = win32gui.GetWindowText(hwnd)

                if text != old_text:
                    version, game = parse_title(text)

                    rpc.update(large_image='icon', large_text=f'Nintendo 3DS emulator {version}',
                               state='Idling' if game is None else 'In-game', details=game, start=start)

                    old_text = text

                time.sleep(1)
        finally:
            cv_closed = True

            rpc.clear()
            rpc.close()


def connect():
    win32gui.EnumWindows(enum_callback, 0)

    if not found_window:
        print('Discord RPC: waiting for Citra Valentin to start...')

        while not cv_closed:
            win32gui.EnumWindows(enum_callback, 0)


if __name__ == '__main__':
    connect()
