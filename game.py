import questionary
import time
import sys
import os
import contact_boss
import curses

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def undertail_1(text, speed=0.4):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)

    print()

def undertail_2(text, speed=0.2):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)

    print()

def undertail(text, speed=0.07):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)

    print()

##############

time.sleep(2)
print("\n\n\n")

#Line 1
undertail_1("Are you...\n")
undertail_2("There?")


time.sleep(2)
print("\n\n\n")


#Line 2
undertail_1("Are we...\n")
undertail_2("Connected?")


time.sleep(4)
print("\n\n\n")


#Line 3
undertail_2("Excellent.")


time.sleep(2)
print("\n\n\n")


undertail_1("Truly\n")
undertail_2("Excellent.")

time.sleep(1)
print("\n\n\n")


#Line 4
undertail_1("Now.\n")
time.sleep(1)
undertail_1("We may begin.")

time.sleep(4)
print("\n\n\n")


time.sleep(2)
clear()


#Line 5
undertail_2("You Must Create\n\n\n")
time.sleep(1)
undertail_2("A vessel.")


#"player creation"

while True:

#body

#head
    undertail("Choose a head for the vessel.")
    time.sleep(3)
    print("\n\n\n")


    head_choice = questionary.select(
    "Select the head that you prefer.",
    choices=[
        "Head 1",
        "Head 2",
        "Head 3",
        "Head 4",
        "Head 5",
        "Head 6",
        "Head 7",
        "Head 8"
        
    ],
    pointer = "*"
    ).ask()

    undertail(f"{head_choice}?")
    time.sleep(1)
    undertail_2("Good choice.")


    time.sleep(2)


#torso
    torso_choice = questionary.select(
    "Select the torso that you prefer.",
    choices=[
        "Torso 1",
        "Torso 2",
        "Torso 3",
        "Torso 4",
        "Torso 5",
        "Torso 6",
        "Torso 7",
        "Torso 8"
        
    ],
    pointer = "*"
    ).ask()

    undertail(f"{torso_choice}?")
    time.sleep(1)
    undertail_2("Good choice.")


    time.sleep(2)


#legs
    leg_choice = questionary.select(
    "Select the legs that you prefer.",
    choices=[
        "Legs 1",
        "Legs 2",
        "Legs 3",
        "Legs 4",
        "Legs 5",
        "Legs 6",
        "Legs 7",
        "Legs 8"
        
    ],
    pointer = "*"
    ).ask()

    undertail(f"{leg_choice}?")
    time.sleep(1)
    undertail_2("Good choice.")


    print("\n\n\n")

    #completed?
    undertail_2("This")
    time.sleep(1)
    undertail_2("is your body.")

    time.sleep(2)

    undertail_1("Do you accept it?")

    body_choice = questionary.select(
    "",
    choices=["Yes", "No"],
    pointer="*"
    ).ask()

    if body_choice == "Yes":
        undertail_2("Excellent.")
        break

    elif body_choice == "No":
        continue


#completed
undertail("You have created\n\n\n")
time.sleep(2)
undertail("a wonderful Vessel.")

undertail_2("Now.")
time.sleep(1)

#mind shaping
undertail_1("Let us shape its mind")
time.sleep(1)
undertail_1("as your own.")

while True:
    #food

    undertail_2("What is its favorite food?")

    food_choice = questionary.select(
        "",
        choices=["Sweet", "Soft", "Sour", "Salty", "Pain", "Cold"],
        pointer="*"

    ).ask()

    #blood type

    undertail_2("Your favorite blood type?")

    blood_choice = questionary.select(
        "",
        choices=["A", "AB", "B", "C", "D"],
        pointer="*"
    ).ask()


    #color 

    undertail_2("What color does it like most?")

    color_choice = questionary.select(
        "",
        choices=["Red", "Blue", "Green", "Cyan"],
        pointer="*"
    ).ask()

    #gift

    undertail_2("Please give it")
    time.sleep(1)
    undertail_2("a gift.")

    gift_choice = questionary.select(
        "",
        choices=["Kindness", "Mind", "Ambition", "Bravery", "Voice"],
        pointer="*"
    ).ask()

    #feeling

    undertail_2("How do you feel about your creation?\n(It will not hear.)")

    feeling_choice = questionary.select(
        "",
        choices=["Love", "Hope", "Disgust", "Fear"],
        pointer="*"
    ).ask()

    #mind shaping complete?
    undertail_2("Have you answered honestly?")

    honest_choice = questionary.select(
        "",
        choices=["Yes", "No"],
        pointer="*"
    ).ask()

    if honest_choice == "No":
        continue

    undertail_2("You acknowledge the possiblity of pain and seizure.")

    pain_choice = questionary.select(
        "",
        choices=["Yes", "No"],
        pointer="*"
    ).ask()

    if pain_choice == "Yes":
        break

    elif pain_choice == "No":
        continue


undertail_1("Understood.")
time.sleep(2)
print("\n\n\n")

#name
undertail("Name your vessel.")
name = input("* ")

if name.casefold() == "gaster":
    raise RuntimeError("AN UNEXPECTED ERROR HAS OCCURRED")

elif name in [
    "kris", "susie", "noelle", "berdly",
    "catti", "jockington", "rudy",
    "asriel", "toriel", "asgore",
    "alphys", "undyne", "bratty",
    "catty", "sans", "gerson",
    "qc", "papyrus"
]: 
    undertail(f"{name}. An interesting coincidence.")

else:
    time.sleep(2)
    undertail_2(f'We called it "{name}."')

#creator name
undertail("And what about")
time.sleep(1)
print("\n")
undertail("the Creator?")

creator_name = input("* ")

if creator_name == name:
    undertail_1("OF COURSE OF COURSE.")
    undertail("OF COURSE THEY ARE THE SAME.")

elif creator_name in [
    "Kris", "Susie", "Noelle"
]:
    undertail("You are about to meet someone")
    time.sleep(1)
    print("\n\n")
    undertail_2("very")
    time.sleep(1)
    print("\n\n")
    undertail_2("very")
    time.sleep(1)
    print("\n\n")
    undertail("wonderful.")

elif creatore_name in [
    "kris", "susie", "noelle", "berdly",
    "catti", "jockington", "rudy",
    "asriel", "toriel", "asgore",
    "alphys", "undyne", "bratty",
    "catty", "sans", "gerson",
    "qc", "papyrus"
]:
    undertail_2(f"{name}. How interesting.")

else:
    undertail_2(f'"{creator_name}."')
    time.sleep(2)


undertail_2("Excellent.")


time.sleep(2)
print("\n\n\n")


undertail_1("Truly\n")
undertail_2("Excellent.")

time.sleep(3)
print("\n\n\n")

undertail_2(f'"{creator_name}."')
time.sleep(1)

undertail_2("Thank you")
time.sleep(1)
undertail_1("for your time.")

time.sleep(2)

undertail_2("Your answers")
time.sleep(3)

undertail_2("Your wonderful")
time.sleep(1)
undertail_1("creation")

time.sleep(1)
clear()
time.sleep(1)

undertail_2("Will now be\n")
time.sleep(2)
undertail_2("discarded.")

time.sleep(5)
undertail_2("CONTACT ESTABLISHED")

curses.wrapper(contact_boss.main)