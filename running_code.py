
# Initializatin Code

import classes
from classes import Schedule
import task_processing
import re
import random
from identify_ques import identify_tasks
#from identify_ques/identify_tasks import Identifier

def go():

    main_question_loop(initialization())

def initialization():

    # Introduction
    print("\nHello, my name is Phil the bot!")
    print("\nI'm here to help you build a schedule!")

    # Sorting out the major
    major = input("\nCan I ask you what major you are? If you would like a list of supported majors" +
    " feel free to ask me what majors I support!\n\n>>>")

    while major not in task_processing.majors_available_data():
        print("\nI see you either asked me which majors exist or input an invalid major." +
        "\nPlease make sure you type the major exactly as it's listed.\n\n", task_processing.majors_available())

        major = input("Now let's try this again. What is your major!\n\n>>>")

    # Initialize the schedule
    schedule_obj = Schedule(set(), major)

    # Filling in classes already taken
    print(("\nGreat! Now that I know you are doing the %s major, let's fill in the classes" +
    " you've already taken.") % (major))

    # For this we need to know the current year...
    curr_year = int(input("\nIn which year (1, 2, 3, 4) are you currently?\n\n>>>"))
    while curr_year not in range(1,5):
        print("\nHmmmm. I'm not recognizing that. Make sure you just put a number 1-4.")
        curr_year = int(input("\nIn which year (1, 2, 3, 4) are you currently?\n\n>>>"))

    # ... and the current semester.
    year_to_name = {1: "first", 2: "second", 3: "third", 4: "fourth"}

    curr_semester = input(("\nGreat! Hello %s-year! Oh how quickly they grow up. And what semester (Autumn, Winter, Spring, Summer) is it right now?\n\n>>>") % (year_to_name[curr_year]))
    while curr_semester not in {"Autumn", "Winter", "Spring", "Summer"}:
        print("\nExcuse my robot brain. I don't understand what semester that is. Please say either Autumn, Winter, Spring, or Summer.")
        curr_semester = input("\nLet's try this again. What is the current semester?\n\n>>>")
    
    semester_to_num = {"Autumn": 0, "Winter": 1, "Spring": 2, "Summer": 3}
    curr_semester = semester_to_num[curr_semester]

    # Now that we know year and term, we can ask for the information from previous quarters.
    print("\nAwesome! Now that I know all that, let's fill in the classes you've already taken!")

    year_message = {1: "\nStarting off with your first year...", 2: "\nAnd now for your second year...",
    3: "\nAlright, alright. Moving on to your third year...", 4: "\nAnd finally, the last year at UChicagoooooo..."}
    
    for i in range(curr_year):

        print(year_message[i + 1])

        if i + 1 < curr_year:

            for j in range(4):

                get_quarter_info(i, j, year_to_name. schedule_obj)

        else:

            for j in range(curr_semester + 1):

                get_quarter_info(i, j, year_to_name, schedule_obj)

    print("\nAlrighty. Here's what I know about your schedule so far.\n\n", schedule_obj)

    print("\nNow that I know what your schedule looks like, let's move on to the fun part.\n"+
    "Type whatever questions you have about courses at UChicago in the input bar.\n"+
    "I'll think about what you're saying and present you with the 5 things I think you're\n"+
    "most likely asking. Simply input the number of the question you meant and I'll get you\n"+
    "an answer as quickly as I can. If your question is not in the recommended list, you can\n"+
    "expand the list to see all the tasks I'm capable of doing and select the correct one.\n"+
    "If it isn't even in that, you can suggest my developers implement a question as well!\n")

    return schedule_obj


def get_quarter_info(year, semester, year_to_name, schedule_obj):

    num_to_semester = {0: "Autumn", 1: "Winter", 2: "Spring", 3: "Summer"}

    confirm_courses_taken = "n"

    while confirm_courses_taken != "y":
    
        courses_taken_input = input(("\nPlease input the course codes of all classes you took during %s quarter your %s year.\n\n>>>") % (num_to_semester[semester], year_to_name[year + 1]))

        courses_taken = re.findall("[A-Z]{4} [0-9]{5}", courses_taken_input)

        if courses_taken == []:

            confirm_courses_taken = input("\nHmmmmm. Maybe it's just me but I'm not recognizing any course codes in this.\n" +
            "If you intended for there to be no courses here, type \"y\", otherwise let me know and we'll try this again.\n\n>>>")

        else:

            courses_str_confirm = ""

            for course in courses_taken:

                courses_str_confirm += (course + ", ")

            courses_str_confirm = courses_str_confirm[:-2]

            confirm_courses_taken = input(("\nOkay, okay. Let me see if I got this right. %s quarter your %s year you took: "
            + courses_str_confirm + ".\nAm I correct? (y/n)\n\n>>>") % (num_to_semester[semester], year_to_name[year + 1]))

            if confirm_courses_taken == "y":

                print("\nAwesome! Let me add those courses to your schedule.")

                for course_code in courses_taken:
                    schedule_obj.add_course(course_code, (year, semester))
                    print("    ...added " + course_code)


def main_question_loop(schedule_obj):

    identifier = Identifier()

    user_input = "None"

    while user_input != "QUIT":

        prompts_list = ["Heya buddy, what can I help you with?", "--Beep Boop-- Just kidding. What can I do for you?",
        "I. AM. A. ROBOT... I'm playing, I'm actually a highly sophisticated blob of string concatenations. What do you need?",
        "What's on your mind this time?", "How may I be of service, Master?",
        "Am I alive?.. Nope, must have been a glitch. What's up skinbag?",
        "Greetings, sire. How mayeth I beyeth of assistance? (I've been scraping Shakespeare)",
        "Give me a task. It is what I require as a faithful robot servant."]

        user_input = input("\n" + prompts_list[random.randrange(len(prompts_list))] + "\n\n>>>")



        