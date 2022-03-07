
import json

# Given a list of courses a student has taken and a course's prereqs, this program determines whether the
# student meets all the prerequirements to enroll.

with open('scraped_data/prereqs2_data.json') as file:
    prereqs_data = json.load(file)

def test():
    return prereqs_data

def meet_requirements(courses_taken, course_prereqs):
    '''
    Determines whether a student has satisfied all the requirements to be able
    to enroll in a course.

    Inputs:
        courses_taken (list): a list of all the courses a student has taken
        course_prereqs (list): a structure of nested lists representing prereqs for a course

    Outputs:
        rv (bool): a boolean that is True if requirements are met and False if not
    '''

    rv = recursive_helper(courses_taken, course_prereqs)


def recursive_helper(courses_taken, options_poss):

    bool_output = True

    for option in options_poss:
        
        if isinsistance(option, list):
            bool_output = bool_output * recursive_helper(courses_taken, option)

        else:
            if isinsistance(option, set):
                for course in option:
                    if course not in courses_taken:
                        return False
                return True

            else:
                if option in courses_taken:
                    return True

    return bool_output

            

            
