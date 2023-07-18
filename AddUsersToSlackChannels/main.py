from utils import automation, file, get, gui, common


def main():
    accounts_file = file.get()
    sheet = accounts_file.active
    
    emails_index = get.emailsColumnIndex(sheet)
    channels_index = get.channelNameColumnIndex(sheet)

    if channels_index != None and emails_index != None:
        channels_dict = get.channelsDict(sheet)

        answer = ""            
        
        spaces = "========================"
        common.cprint(
            "\n\n{0} ATTENTION {0}\n".format(spaces),
            "light_red",
            attrs=["bold"]
        )
        print("The automation process will start now!\n"+
            "But first make sure to attend to all the items that will be displayed bellow!\n\n"
        )
        for question_index in range(0, len(common.QUESTIONS)):
            if common.answerCheck(answer):
                common.cprint( # this is a function on termcolor module to add colors and formatting to python console
                    "({}/{}) {}".format(
                        question_index + 1,
                        len(common.QUESTIONS),
                        common.QUESTIONS[question_index]
                    ), 
                    "light_yellow",
                    attrs=["bold"]
                )
        
                print("----> Hit", end=" ")
                common.cprint(
                    "'enter'", 
                    "light_grey", 
                    attrs=["underline"], 
                    end=" "
                )
                print("if this step was completed")
                
                print("----> Type", end=" ")
                common.cprint(
                    "'n'", 
                    "light_grey",
                    attrs=["underline"],
                    end=" "
                )
                print("to cancel automation ")
                answer = input(common.cprint("--> ", attrs=["bold"], end=""))
                common.clearConsole()
        
        if common.answerCheck(answer):
            sleep = 5 # seconds to wait for the automation to start
            common.cprint("DON'T SWITCH BACK TO SLACK", "red", attrs=["bold"])
            common.cprint("DON'T TOUCH THE KEYBOARD OR MICE", "red", attrs=["bold"])
            print("\nGo grab a coffee and come back again to check up if everything is working fine")
            common.cprint("Automation will start in {} seconds!".format(sleep), "light_yellow", attrs=["bold"])
            gui.printlessCountdown(sleep)
            automation.start(channels_dict)
    else:
        common.cprint("Your sheet doesn't have a 'Channel Name' or a 'User E-Mail' header\n"+
                "Please, check 'model.xlsx' and correct you channels file",
                "light_red"
        )


if __name__ == "__main__":

    if file.exists():
        common.cprint("File found!", "light_green", attrs=["bold"])
        common.printLine()

        main()
    else:
        text = common.colored("Channels file wasn't found.\n","light_red",attrs=["bold"]) + "Please, make sure to create a "+ common.colored("new file ", attrs=["bold"]) + "or " + common.colored("rename ", attrs=["bold"]) + "the file you put the e-mails to "+ common.colored("'accounts.xlsx'", "light_yellow", attrs=["underline"]) + "!\n" + "Also make sure that it is " + common.colored("structurally equal ", attrs=["bold"]) + "to " + common.colored("'model.xlsx'", "light_yellow", attrs=["underline"]) + " present in this project folder."
        print(text)
    
    common.exitingProgram()