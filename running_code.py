
# Initializatin Code

import classes
from classes import Schedule
import task_processing

def initialization():

    print("\nHello, my name is Phil the bot!")

    print("\nI'm here to help you build a schedule!")

    major = input("\nCan I ask you what major you are? If you would like a list of supported majors" +
    " feel free to ask me what majors I support! ")

    schedule_obj = Schedule(set(), major)

    classes_taken = "n"

    while classes_taken != "y":
        classes_taken = input("\nBefore we start though, could I ask you what classes you've already taken? (y/n): ")

    print("\nGreat. Lets get started.")

    done_inputting_classes = "n"

    while done_inputting_classes != "y":

        course_code = input("\nPlease input a class's course code you have already taken: ")

        year_taken = int(input("\nWhat year (1, 2, 3, 4) did you take this course: "))

        semesters_to_years = {"Autumn": 0, "Winter": 1, "Spring": 2, "Summer": 3}

        semester_taken = input("\nWhat semester (Autumn, Winter, Spring, Summer) did you take this course: ")

        can_add = input("\nCan I add %s to your schedule in Year %d, %s semester? (y/n): " % (course_code, year_taken, semester_taken))

        if can_add == "y":
            semester_input = (year_taken, semesters_to_years[semester_taken])
            schedule_obj.add_course(course_code, semester_input, instructor="Not Specified")
            print("\nGreat! I added it for you!")

        done_inputting_classes = input("\nAre you done adding classes to your schedule for now? (y/n) ")

    print(schedule_obj)