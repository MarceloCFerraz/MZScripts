import pyautogui as gui
import time

STANDARD_INTERVAL = 0.1  # interval is used to time the elapsed time between one action to the next (e.g. one key press/click to the next)
STANDARD_DURATION = STANDARD_INTERVAL  # duration is used to determine the general time spent on a action (e.g. move the cursor to the coordinates)


def updatePage():
    gui.hotkey("ctrl", "shift", "r")


def click(x, y):
    # clica nas coordenadas que o botão está para dar foco na janela/fechar qualquer popup
    gui.click(x, y)


def clickSleep(x, y, sleep):
    # clica nas coordenadas que o botão está para dar foco na janela/fechar qualquer popup
    gui.click(
        x,
        y,
        duration=STANDARD_DURATION * 3,  # 0,3s
    )
    time.sleep(sleep)


def rightClickSleep(x, y, sleep):
    gui.rightClick(
        x,
        y,
        STANDARD_DURATION * 5,  # 0,5s
    )
    time.sleep(sleep)


def pressKey(key):
    gui.press(key)


def pressKeySleep(key, sleep):
    gui.press(key)
    time.sleep(sleep)


def hotKeySleep(key_1, key_2, sleep):
    gui.hotkey(key_1, key_2)
    time.sleep(sleep)


def typeSleep(text, seconds):
    gui.typewrite(
        text,
        interval=STANDARD_INTERVAL / 10,  # 0,01s from a key press to the next
    )
    time.sleep(seconds)


def countdown(seconds):
    while seconds > 0:
        # if seconds <= 10:
        #     # emits an alert sound after each second
        #     winsound.Beep(900, 100)
        print(seconds)
        seconds -= 1
        time.sleep(1)


def printlessCountdown(seconds):
    time.sleep(seconds)
