import os

from termcolor import colored, cprint  # noqa: F401

STANDARD_SLEEP_TIME = 1  # seconds

QUESTIONS = [
    "You need to set:\n"
    + "** Monitor Resolution to 1920 x 1080 pixels **\n"
    + "** Screen scale to 100% (windows scale) **\n",
    "You need to use SLACK DESKTOP APP "
    + "AND let its WINDOW MAXIMIZED but not in FULL SCREEN MODE\n",
    "Now please make sure you are at the right Slack Workspace\n"
    + "The workspace should be the account you were assigned to (e.g. MileZero)\n",
    "It is important that you are a member of all the channels on the list. "
    + "If you're not, please join them before continuing\n",
    "Make sure to disable any notifications on your computer. It can "
    + "cause the automation process to not work properly!\n",
    "Make sure to close any Slack THREADS open on the right corner of the app"
    "Make sure that slack is open and that \n"
    + "-> (Windows) its shortcut is pinned at the 4th position on the task bar! "
    + "If the position is different or the program isn't open, nothing will work!\n"
    + "-> (Mac and Linux) you are prepared to jump back to Slack after this question. "
    + "You'll have 5 seconds to do so after pressing ENTER now but try to do it as fast as you can\n",
]


def printLine():
    print("--------------------------------------------")


def printChannelsDict(channels_dict):
    for key in channels_dict.keys():
        print("{} ({} channels): ".format(key, len(channels_dict[key])), end="")
        print(channels_dict[key])
        printLine()


def exitingProgram():
    print("\nExiting program...")


def answerCheck(answer):
    return answer == "" or answer.capitalize() == "Y"


def clearConsole():
    if os.name == "posix":
        os.system("clear")
    else:
        os.system("cls")
