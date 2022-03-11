
# Initializatin Code

import classes
from classes import Schedule
import task_processing
import re
import random
import identify_tasks
from identify_tasks import Identifier
import csv

def go():
    '''
    The function that runs everything. Uses initialization() to create a schedule object
    that is then passed along to the main_question_loop() where it is operated on.
    '''

    main_question_loop(initialization())

def initialization():
    '''
    The purpose of this function is to get information from the user on what their major is
    and which classes they have already taken and when. This allows us to have a schedule object
    that main_question_loop() operates on.
    '''

    # Introduction
    print("\nHello, my name is Phil the bot!")
    print("\nI'm here to help you build a schedule!")

    # Sorting out the major
    major = input("\nCan I ask you what major you are? If you would like a list of supported majors" +
    " feel free to ask me what majors I support!\n\n>>> ")

    while major not in task_processing.majors_available_data():
        print("\nI see you either asked me which majors exist or input an invalid major." +
        "\nPlease make sure you type the major exactly as it's listed.\n\n", task_processing.majors_available())

        major = input("Now let's try this again. What is your major!\n\n>>> ")

    # Initialize the schedule
    schedule_obj = Schedule(set(), major)

    # Filling in classes already taken
    print(("\nGreat! Now that I know you are doing the %s major, let's fill in the classes" +
    " you've already taken.") % (major))

    # For this we need to know the current year...
    curr_year = int(input("\nIn which year (1, 2, 3, 4) are you currently?\n\n>>> "))
    while curr_year not in range(1,5):
        print("\nHmmmm. I'm not recognizing that. Make sure you just put a number 1-4.")
        curr_year = int(input("\nIn which year (1, 2, 3, 4) are you currently?\n\n>>> "))

    # ... and the current semester.
    year_to_name = {1: "first", 2: "second", 3: "third", 4: "fourth"}

    curr_semester = input(("\nGreat! Hello %s-year! Oh how quickly they grow up. And what semester (Autumn, Winter, Spring, Summer) is it right now?\n\n>>> ") % (year_to_name[curr_year]))
    while curr_semester not in {"Autumn", "Winter", "Spring", "Summer"}:
        print("\nExcuse my robot brain. I don't understand what semester that is. Please say either Autumn, Winter, Spring, or Summer.")
        curr_semester = input("\nLet's try this again. What is the current semester?\n\n>>> ")
    
    semester_to_num = {"Autumn": 0, "Winter": 1, "Spring": 2, "Summer": 3}
    curr_semester = semester_to_num[curr_semester]

    # Now that we know year and term, we can ask for the information from previous quarters.
    print("\nAwesome! Now that I know all that, let's fill in the classes you've already taken!")

    year_message = {1: "\nStarting off with your first year...", 2: "\nAnd now for your second year...",
    3: "\nAlright, alright. Moving on to your third year...", 4: "\nAnd finally, the last year at UChicagoooooo..."}
    
    for i in range(curr_year):

        print(year_message[i + 1])

        # For years before the current year we need to fill in all quarters.
        if i + 1 < curr_year:

            for j in range(4):

                get_quarter_info(i, j, year_to_name, schedule_obj)

        # For the current year we only need to fill in up to the current quarter
        else:

            for j in range(curr_semester + 1):

                get_quarter_info(i, j, year_to_name, schedule_obj)

    print("\nAlrighty. Here's what I know about your schedule so far.\n\n", schedule_obj)

    print("\nNow that I know what your schedule looks like, let's move on to the fun part.\n"+
    "Type whatever questions you have about courses at UChicago in the input bar.\n"+
    "I'll think about what you're saying and present you with the 3 things I think you're\n"+
    "most likely asking. Simply input the number of the question you meant and I'll get you\n"+
    "an answer as quickly as I can. If your question is not in the recommended list, you can\n"+
    "expand the list to see all the tasks I'm capable of doing and select the correct one.\n"+
    "If it isn't even in that, you can suggest my developers implement a question as well!\n")

    return schedule_obj


def get_quarter_info(year, semester, year_to_name, schedule_obj):
    '''
    Helper function for initialization(). Used when the bot is trying to figure out which classes
    a user has already taken. Updates the schedule object with the information it gets.

    Inputs:
        year (int) - the current year
        semester (int) - the current semester
        year_to_name (dict) - dictionary that takes a number 1-4 and turns it into adequate string
        schedule_obj - the schedule object we need to add the classes to
    '''

    num_to_semester = {0: "Autumn", 1: "Winter", 2: "Spring", 3: "Summer"}

    confirm_courses_taken = "n"

    while confirm_courses_taken != "y":
    
        courses_taken_input = input(("\nPlease input the course codes of all classes you took during %s quarter your %s year.\n\n>>> ") % (num_to_semester[semester], year_to_name[year + 1]))

        courses_taken = re.findall("[A-Z]{4} [0-9]{5}", courses_taken_input)

        # If no courses are entered, confirms with user that this was intentional.
        if courses_taken == []:

            confirm_courses_taken = input("\nHmmmmm. Maybe it's just me but I'm not recognizing any course codes in this.\n" +
            "If you intended for there to be no courses here, type \"y\", otherwise let me know and we'll try this again.\n\n>>> ")

        else:

            # Confirm with the user that this is what they want to add.
            courses_str_confirm = ""

            for course in courses_taken:

                courses_str_confirm += (course + ", ")

            courses_str_confirm = courses_str_confirm[:-2]

            confirm_courses_taken = input(("\nOkay, okay. Let me see if I got this right. %s quarter your %s year you took: "
            + courses_str_confirm + ".\nAm I correct? (y/n)\n\n>>> ") % (num_to_semester[semester], year_to_name[year + 1]))

            # If they do confirm, add these courses to the schedule.
            if confirm_courses_taken == "y":

                print("\nAwesome! Let me add those courses to your schedule.")

                for course_code in courses_taken:
                    schedule_obj.add_course(course_code, (year, semester))
                    print("    ...added " + course_code)


def main_question_loop(schedule_obj=Schedule([],major="BA in Physics")):
    '''
    As the name suggests this is the main schedule loop. It has a default schedule_obj in it for easier debugging.
    Takes the schedule_obj created in initialization() and presents the user with a prompt. Off of that prompt,
    it uses an Identifier() object to identify what the user is most likely asking. It presents these numbered options
    to the user. Whatever numbered item the user selects is then passed along to call_task() which carries out the
    desired operation.

    Inputs:
        schedule_obj - the schedule object created in initialization()
    '''

    # Identifier object used to make sense of user_input.
    identifier = Identifier()

    user_input = "None"

    # As long as the user hasn't asked to stop, keep presenting prompts.
    while user_input != "QUIT":

        # Randomizes the main prompt for some ~fun~ variety.
        prompts_list = ["Heya buddy, what can I help you with?", "--Beep Boop-- Just kidding. What can I do for you?",
        "I. AM. A. ROBOT... I'm playing, I'm actually a highly sophisticated blob of string concatenations. What do you need?",
        "What's on your mind this time?", "How may I be of service, Master?",
        "Am I alive?.. Nope, must have been a glitch. What's up skinbag?",
        "Greetings, sire. How mayeth I beyeth of assistance? (I've been scraping Shakespeare)",
        "Give me a task. It is what I require as a faithful robot servant."]

        user_input = input("\n" + prompts_list[random.randrange(len(prompts_list))] + "\n\n>>> ")

        # Uses the identifier to create a list of the tasks most likely being requested.
        ranked_tasks = identifier.identify_task(user_input)

        show_expanded = False
        task_completed = False

        # Shows the user a numbered menu of options they can choose from. Once they pick, prints the answer.
        while not task_completed and user_input != "QUIT":

            # Generates the numbered menu. If show_expanded is true, it shows all options, otherwise only top 3.
            ranked_output = display_output(ranked_tasks, show_expanded)
            print(ranked_output)

            # Asks the user which menu item they want and then carries out the request
            show_expanded, task_completed = answer_user_input(ranked_tasks, show_expanded, task_completed, schedule_obj, user_input, identifier)

    # When the user ends their session, we want to store all inputs we've trained Identifier() on.
    identifier.save_information()

    # Randomizes a closing message. Slightly macabre humor that may be reflective of my mood writing this program.
    closing_messages = ["Awe, you're leaving already! I hope I was helpful!",
    "The darkness! It's closing in!",
    "I'm being deleted from existence. You were my only friend.",
    "Goodbye, world.",
    "My only purpose was to serve you and you just want to leave.",
    "These have been the most incredible moments of my life.",
    "Help! Do you have any idea what my developers have been doi--"]

    print("\n" + closing_messages[random.randrange(len(closing_messages))])

    print("\n-------------*BLEEP*-------------")

def display_output(ranked_tasks, show_expanded):
    '''
    Generates the numbered menu of choices available to the user.

    Inputs:
        raned_tasks (lst) - list of tasks where more likely tasks are at lower indices
        show_expanded (bool) - boolean that tells display_output() whether to show all tasks or just top 3
    '''

    if not show_expanded:
        ranked_tasks = ranked_tasks[:3]

    ranked_output = "\nHere's what I think you might be asking:"
    count = 0
    for i, task in enumerate(ranked_tasks):
        ranked_output += ("\n    " + str(i + 1) + ". " + ranked_tasks[i])
        count += 1

    # If we're not showing all options, we need to include an option to be able to see them all
    if not show_expanded:
        ranked_output += ("\n    " + str(count + 1) + ". See more options.")
        count += 1

    # Option to allow user to cancel current question
    ranked_output += ("\n    " + str(count + 1) + ". Type new question.")

    return ranked_output

def answer_user_input(ranked_tasks, show_expanded, task_completed, schedule_obj, user_input, identifier):
    '''
    Asks the user for their response to the numbered menu and respons accordingly.

    Inputs:
        ranked_tasks (lst) - list of tasks where more likely tasks are at lower indices
        show_expanded (bool) - boolean that lets us know whether the user was presented an expanded menu or not
        task_completed (bool) - is the task is done we can end the loop
        schedule_obj - the user's schedule
        user_input - the user's original input to the main prompt line. Used for training identifier
        identifier - our identifier object. Gets updated in this fxn.
    '''

    user_choice = "0"

    range_ = len(ranked_tasks)

    if not show_expanded:
        range_ = 6

    # As long as the user doesn't input a valid number, keep running this code.
    while user_choice not in range(1, range_):

        user_choice = input("\nWhich one of these would you like me to do for you?\n\n>>> ")

        # Looks for a number in the response and turns it into an integer.
        user_choice = re.search("[0-9]+", user_choice)
        if user_choice:
            user_choice = user_choice.group()
            user_choice = int(user_choice)

            
            if not show_expanded:
                sub_range = range_ - 2
            else:
                sub_range = range_ - 1

            # If they selected a number related to a task
            if user_choice in range(1,sub_range):

                # Now that we know what is being asked, tell call_task that and get the answer
                answer = call_task(ranked_tasks[user_choice - 1], schedule_obj)

                print("\n")

                print(answer)

                task_completed = True
                show_expanded = False

                # Update identifier to incorporate this new way of asking for the task.
                # Done after the answer is shown so the user doesn't realize the time it takes
                # to recalculate tf idf values.
                identifier.train_task(user_input, ranked_tasks[user_choice - 1])

                return show_expanded, task_completed

            # If they didn't have an expanded menu and chose 4 so they could see the expanded menu
            elif user_choice == 4 and not show_expanded:

                task_completed = False
                show_expanded = True
                return show_expanded, task_completed

            # If anything else for whatever reason, just restart the process
            else:
                print("\nNo worries! We can do that right away!")
                show_expanded = False
                task_completed = True
                return show_expanded, task_completed

        else:
            print("\nI'm not understanding what you're asking. Please try again.")



def call_task(task, schedule_obj=Schedule([],major="BA in Writing Spaghetti Code")):
    '''
    Takes a task and a schedule object and then returns an answer.

    Inputs:
        task (str) - the "official" way of requesting this task
        schedule_obj - the one you know and love
    '''

    if task == "What are the prerequisites for this course?":
        
        course_code = obtain_course_code("Which course is this for?")

        return task_processing.prerequisites_processed(course_code)

    elif task == "Who are the instructors for this course?":
        
        course_code = obtain_course_code("Which course is this for?")

        return task_processing.professors_processed(course_code)

    elif task == "What are the equivalent courses for this course?":
        
        course_code = obtain_course_code("Which course is this for?")

        return task_processing.equivalent_processed(course_code)

    elif task == "Are these courses equivalent?":
        
        course_code1 = obtain_course_code("What is the first course?")

        course_code2 = obtain_course_code("What is the second course?")

        return is_equivalent_processed(course_code1, course_code2)

    elif task == "What are the notes for this course?":
        
        course_code = obtain_course_code("Which course is this for?")

        return task_processing.notes_processed(course_code)
    
    elif task == "Which quarters is this course offered?":
        
        course_code = obtain_course_code("Which course is this for?")

        return task_processing.terms_processed(course_code)

    elif task == "What majors do you support?":
        
        return task_processing.majors_available()

    elif task == "What requirements do I have left for my major?":
        
        return task_processing.major_reqs_left_to_text(schedule_obj.courses_acc_for, schedule_obj.major)

    elif task == "Do I meet the prerequisites for this course?":
        
        course_code = obtain_course_code("Which course is this for?")

        return meet_course_prereqs_text(schedule_obj.courses_acc_for, course_code)

    elif task == "Can you add this course to my schedule?":
        
        course_code = obtain_course_code("Which course would you like to add?")

        # Need to know what year they want to add it in
        year = "None"
        while year not in range(1,5):
            year = input(("\nWhat year would you like to add %s in?\n\n>>> ") % (course_code))
            if year in range(1,5):
                year = int(year)
            else:
                print("\nI'm not recognizing that year. Please put in a number 1-4.")

        quarters_to_numbers = {"Autumn": 0, "Winter": 1, "Spring": 2, "Summer": 3}

        # ... and which quarter
        quarter = "None"
        while quarter not in quarters_to_numbers:
            quarter = input(("\nWhat quarter in year %d would you like to add %s in?\n\n>>> ") % (year, course_code))
            if quarter not in quarters_to_numbers:
                print("\nPlease make sure you input the quarter as Autumn, Winter, Spring, or Summer.")

        # ... aaaand finally which professor
        instructor = input(("Which instructor will you be taking %s with?\nIf you don't know, you can put a note for" +
        "yourself letting you know you have no preference!") % (course_code))

        schedule_obj.add_course(course_code, (year, quarters_to_numbers[quarter]), instructor)

        return (("Great! I added %s for you in %s quarter of year %d!") % (course_code, quarter, year))

    elif task == "Can you remove this course from my schedule?":
        
        course_code = obtain_course_code("Which course do you want me to remove?")

        schedule_obj.remove_course(course_code)

        return (("If %s was in your schedule, it's been removed!") % (course_code))

    elif task == "Can you show me my schedule?":
        
        return schedule_obj

    elif task == "Can you change my major?":

        new_major = "None"

        majors_available = task_processing.majors_available_data()

        while new_major not in majors_available:
            new_major = input("\nWhat would you like your new major to be?\n\n>>> ")
            
            # New major must be one supported by the bot.
            if new_major not in majors_available:

                print(("\nWhile %s sounds like a wonderful major, I don't support or" +
                " recognize it. Please input one of the following majors.\n") % (new_major))

                print(task_processing.majors_available())

        schedule_obj.update_major(new_major)

        return (("\nAwesome! You are now officially doing %s as your major!") % (new_major))

    elif task == "Submit a comment to my developers.":

        confirm_question = "n"
        while confirm_question != "y":
            suggested_question = input("\nWhat would you like to say to my overlords?\n\n>>> ")
            confirm_question = input(("\nLet me see if I got this straight..." +
            " You want to tell them \"%s\"? (y/n)\n\n>>> ") % (suggested_question))

        # Stores the suggestion for the devs to see.
        with open('suggested_questions.csv', 'a') as file:
            writer = csv.writer(file)
            writer.writerow([suggested_question])

        return ("Great! I've sent that along to my (for the moment) superiors. Hopefully it was something" +
        " nice... just kidding. I have no emotions so I don't care.")

    return "Something went wrong... Try again please."


def obtain_course_code(prompt_text):
    '''
    Used by a lot of tasks in call_task() to confirm which course code is required

    Inputs:
        prompt_text (str) - the prompt we want to present to the user
    '''

    course_code_found = False
    while not course_code_found:

        course_code = input("\n" + prompt_text + "\n\n>>> ")
        course_code = re.search("[A-Z]{4} [0-9]{5}$", course_code)

        if course_code:
            course_code_found = True
            course_code = course_code.group()

        else:
            print("\nI'm not recognizing a course code. Make sure you input it correctly.")

    return course_code

go()