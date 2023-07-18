import time, re
from datetime import datetime
from utils import gui, common


COORDINATES = {
    "search_input": (879, 21),
    "channels_menu_tab": (564, 111),
    "only_my_channels": (803, 165),
    "first_channel": (396, 256),
    "members": (1873, 65),
    "add_people": (717, 356),
    "emails_input": (857, 489),
    "from_another_organization": (815, 556),
    "from_another_organization_next": (1198, 750),
    "only_post": (691, 628),
    "only_post_next": (1198, 683),
    "notes": (829, 544),
    "notes_send_invitation": (1198, 703)
}


def openSlack():
    print("Opening Slack...")
    gui.hotKeySleep(
        "win", "4",
        common.STANDARD_SLEEP_TIME / 2 # 0,5s
    )
    
    time.sleep(common.STANDARD_SLEEP_TIME * 2)


def checkIfNeedsRepetition(emailList):
    # if the e-mail provider is not one in your workspaces 
    # e.g "@milezero.com", "@capstonelogistics.com" and "@lean-tech.io"
    # and if one of those were added to the e-mails list for the channel
    # that the script is currently working on, it means that the script
    # must confirm "From other organization" and "Only Post" twice. This
    # is how slack works 🤷🏻‍♂️
    other_providers = []
    common_providers = [
        "@milezero.com",
        "@capstonelogistics.com",
        "@lean-tech.io"
    ]
    common_providers_count = 0

    for email in emailList:
        email_provider = re.search("@[a-zA-Z0-9_.-]+.[a-zA-Z]{2,}", email).group()
        if email_provider in common_providers:
            common_providers_count += 1
        elif email_provider not in other_providers:
            other_providers.append(email_provider)

    return len(other_providers) > 0 and common_providers_count > 0
            

def start(channels_dict):
    start_time = datetime.now()

    openSlack()

    for channel in channels_dict.keys():
        emails = channels_dict[channel]

        # click search input 3x to make sure it the search input was selected
        for i in range (0, 3):
            gui.clickSleep(
                COORDINATES["search_input"][0], # x
                COORDINATES["search_input"][1], # y
                common.STANDARD_SLEEP_TIME / 2 # 0,3s
            )
        # select and delete all text in the search field
        gui.hotKeySleep(
            "ctrl", "a",
            common.STANDARD_SLEEP_TIME / 3 # 0,33s
        )
        gui.pressKey("del")
        # type channel name on search input
        gui.typeSleep(
            channel, # channel name
            common.STANDARD_SLEEP_TIME / 2 # 0,5s
        )
        # press enter to search for it
        gui.pressKeySleep(
            "enter",
            common.STANDARD_SLEEP_TIME # 1s
        )
        # click "Channels" category
        gui.clickSleep(
            COORDINATES["channels_menu_tab"][0], # x
            COORDINATES["channels_menu_tab"][1], # y
            common.STANDARD_SLEEP_TIME / 5 # 0,2s
        )
        # open channel
        gui.clickSleep(
            COORDINATES["first_channel"][0], # x 
            COORDINATES["first_channel"][1], # y
            common.STANDARD_SLEEP_TIME # 1s
        )
        # click members button
        gui.clickSleep(
            COORDINATES["members"][0], # x
            COORDINATES["members"][1], # y
            common.STANDARD_SLEEP_TIME / 5 # 0,5s
        )
        # click add people
        gui.clickSleep(
            COORDINATES["add_people"][0], # x
            COORDINATES["add_people"][1], # y
            common.STANDARD_SLEEP_TIME / 3 # 0,33s
        )
        # click the e-mails input 2x to make sure it was clicked
        for i in range (0, 2):
            gui.clickSleep(
                COORDINATES["emails_input"][0], # x
                COORDINATES["emails_input"][1], # y
                common.STANDARD_SLEEP_TIME / 3 # 0,33s
            )
        for email in emails:
            # type e-mail to add to the channel
            gui.typeSleep(
                email,
                common.STANDARD_SLEEP_TIME / 2 # 0,5s
            )
            # press enter
            gui.pressKeySleep(
                "enter", 
                common.STANDARD_SLEEP_TIME / 3 # 0,33s
            )
        # press enter to go to next section
        gui.pressKeySleep(
            "enter", 
            common.STANDARD_SLEEP_TIME / 3 # 0,33s
        )
        # steps bellow can repeat up to 2 times 👇🏻 (if the e-mail provider is not one in your workspaces e.g "@milezero.com", "@capstonelogistics.com" and "@lean-tech.io")
        repeats = 2 if checkIfNeedsRepetition(emails) else 1
        for i in range (0, repeats):
            # click "From another organization"
            gui.clickSleep(
                COORDINATES["from_another_organization"][0], # x
                COORDINATES["from_another_organization"][1], # y
                common.STANDARD_SLEEP_TIME / 3 # 0,33s
            )
            # click "Next"
            gui.clickSleep(
                COORDINATES["from_another_organization_next"][0], # x
                COORDINATES["from_another_organization_next"][1], # y
                common.STANDARD_SLEEP_TIME / 3 # 0,33s
            )
            # click "Got it" (same position as Next)
            gui.clickSleep(
                COORDINATES["from_another_organization_next"][0], # x
                COORDINATES["from_another_organization_next"][1], # y
                common.STANDARD_SLEEP_TIME / 3 # 0,33s
            )
            # click "Only post"
            gui.clickSleep(
                COORDINATES["only_post"][0], # x
                COORDINATES["only_post"][1], # y
                common.STANDARD_SLEEP_TIME / 3 # 0,33s
            )
            # click "Next"
            gui.clickSleep(
                COORDINATES["only_post_next"][0], # x
                COORDINATES["only_post_next"][1], # y
                common.STANDARD_SLEEP_TIME / 3 # 0,33s
            )
            # type "Requested by dispatcher" on Note text field
            gui.click(
                COORDINATES["notes"][0], # x
                COORDINATES["notes"][1], # y
            )
            gui.hotKeySleep(
                "ctrl", "a",
                common.STANDARD_SLEEP_TIME / 3 # 0,33s
            )
            gui.pressKey("del")
            gui.typeSleep(
                "Requested by dispatcher", # note message
                common.STANDARD_SLEEP_TIME / 5 # 0,2s
            )
            # click "Send invitations" or "Next" (accordingly to the number of repeats)
            gui.clickSleep(
                COORDINATES["notes_send_invitation"][0], # x
                COORDINATES["notes_send_invitation"][1], # y
                common.STANDARD_SLEEP_TIME * 1.5 # 1,5s
            )
        # Press enter
        gui.pressKeySleep(
            "enter",
            common.STANDARD_SLEEP_TIME / 3 # 0,33s
        )
        # Close add member modal by clicking out of it
        gui.clickSleep(
            COORDINATES["members"][0], # x
            COORDINATES["members"][1], # y
            common.STANDARD_SLEEP_TIME / 3 # 0,33s
        )
    end_time = datetime.now()
    elapsed_time = end_time - start_time

    common.cprint("AUTOMATION FINISHED!", "light_red", attrs=["bold"], end=" ")
    print("(Elapsed Time: {})".format(elapsed_time))
    print()
    print("Please just double check if all users were invited by accessing")
    common.cprint("More > Slack Connect > View Invitations", "light_green", attrs=["bold"])
