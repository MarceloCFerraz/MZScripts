import os
import openpyxl

CHANNELS_LIST_DEFAULT_NAME = "accounts.xlsx"


def exists():
    current_dir = os.listdir()
    if CHANNELS_LIST_DEFAULT_NAME in current_dir:
        return True
    return False


def get():
    file = openpyxl.load_workbook(CHANNELS_LIST_DEFAULT_NAME)
    return file
