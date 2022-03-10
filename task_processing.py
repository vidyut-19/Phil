
# The code that answers task requests

import sqlite3
import os
import json
import re
            
'''
To Do

working with _text.csv files
- fxn that returns prereq text [TICK]
- fxn that returns notes text [TICK]
- fxn that returns equivalents text [TICK]
- fxn that returns terms offred text [TICK]
- fxn that returns an instructors email [TICK]

working with _data.csv files
- fxn that confirms whether a course is offered in a certain term [TICK]
- fxn that confirms whether a course is an equivalent for another [TICK]
- fxn that returns the full names of the professors teaching [TICK] (done in professors_processed)

'''

connection = sqlite3.connect("scraped_data/data.db")
c = connection.cursor()

def prerequisites(course):
    """
    fxn that returns prerequisites raw text
    """

    query = "SELECT prereq_text\nFROM prereqs1_text\nWHERE course = ?"
    params = (course,)
    r = c.execute(query, params)

    return r.fetchall()


def prerequisites_processed(course):
    """
    Formats the info about prerequisites appropriately.
    """

    results = prerequisites(course)

    if bool(results):
        text = results[0][0]
        if text == "!NONE" or text == "undefined" or text == "prereq_text":
            return ("The course catalog doesn't list any prerequisites for " + course + ".")
        else:
            string = "The course catalog says this about the prerequisites for " + course + ":\n"
            return (string + text)
    else:
        return ("I'm sorry, I couldn't recognize the course code: " + course + ".")


def professors(course):
    """
    fxn that returns professor email raw text
    """
    query = "SELECT ie.professor_email, ifn.professor_full_name\nFROM instructor_emails as ie\nJOIN instructors_full_names as ifn ON ifn.professor_full_name = ie.professor_name\nJOIN ins_data2 as id2 ON id2.professor_name = ifn.professor_name\nWHERE id2.course = ?"
    
    params = (course,)
    r = c.execute(query, params)
    
    return r.fetchall()


def professors_processed(course):
    """
    Formats the information about the instructors for a course appropriately.
    """

    results = professors(course)
    results1 = set(results)

    did_it_print = False

    if not bool(results):
        return "I'm sorry, I couldn't recognize the course code: " + course + "."
    elif len(results1) == 1:
        email, name = results[0]
        if email != "UNKNOWN" and name != "Unknown":
            string = "You can reach the instructor for " + course + ", " + name + ", at " + email + "."
            return string
        elif name != "Unknown":
            string = "The instructor for " + course + " is " + name + "."
            return string
    else:
        big_lst = []
        small_lst = []
        for email, name in results1:
            if email != "UNKNOWN" and name != "Unknown":
                big_lst.append((name, email))
                small_lst.append(name)
            elif name != "Unknown":
                small_lst.append(name)
        string = "The instructors for " + course + " are: " + ", ".join(small_lst) + "."
        if len(big_lst) == 1:
            name, email = big_lst[0]
            return string + " You can reach " + name + " at " + email + "."
        elif len(big_lst) > 1:
            lst = []
            for name, email in big_lst:
                lst.append(name + " at " + email)
            string2 = ", ".join(lst)
            return string + " You can reach " + string2 + "."
            

    return "I'm sorry, I'm not sure who the instructors for " + course + " are."


def equivalent(course):
    """
    fxn that returns raw equivalent courses text
    """

    connection = sqlite3.connect("scraped_data/data.db")
    c = connection.cursor()
    query = "SELECT equivalent_course\nFROM equivalent_data\nWHERE course = ?" 
    params = (course,)
    r = c.execute(query, params)
    
    return r.fetchall()


def equivalent_processed(course):
    """
    formats equivalent course text appropriately
    """

    results = equivalent(course)

    if bool(results):
        string = "The equivalent courses to " + course + " are: "
        fixed = [course[0] for course in results]
        string += ", ".join(fixed)
        return (string)
    elif not bool(notes(course)):
        return ("I'm sorry, I couldn't recognize the course code: " + course + ".")
    else:
        return ("It doesn't look like the course catalog lists any equivalent courses for " + course + ".")


def is_equivalent(course1, course2):
    """
    fxn that returns True if the two input courses are equivalent to each
    other, False otherwise
    """

    rv = False

    results1 = equivalent(course1)
    results2 = equivalent(course2)

    r1 = [course[0] for course in results1]
    r2 = [course[0] for course in results2]

    if course1 in r2:
        rv = True
    if course2 in r1:
        rv = True
    
    return rv

def is_equivalent_processed(course1, course2):

    if course1 == course2:
        return ("Nice try. Those are the same course! You're not fooling me that easily.")

    are_equi = is_equivalent(course1, course2)

    if are_equi:
        return (("%s and %s are equivalent courses!") % (course1, course2))

    else:
        return (("%s and %s are not equivalent courses.") % (course1, course2))


def notes(course):
    """
    fxn that returns notes raw text
    """

    connection = sqlite3.connect("scraped_data/data.db")
    c = connection.cursor()
    query = "SELECT note\nFROM notes_text\nWHERE course = ?" 
    params = (course,)
    r = c.execute(query, params)
    
    return r.fetchall()


def notes_processed(course):
    """
    Returns the notes about a course formatted appropriately
    """

    results = notes(course)
    
    if bool(results) and bool(results[0][0]):
        text = results[0][0].strip()
        string = "Here's what the course catalog has to say about " + course + ":\n"
        return (string + text)
    elif bool(results):
        return ("It doesn't look like the course catalog has any notes about " + course + ".")
    else:
        return ("I'm sorry, I couldn't recognize the course code: " + course + ".")


def terms(course):
    """
    fxn that returns terms raw text
    """

    connection = sqlite3.connect("scraped_data/data.db")
    c = connection.cursor()
    query = "SELECT term_data\nFROM terms_data\nWHERE course = ?"
    params = (course,)
    r = c.execute(query, params)
 
    return r.fetchall()


def terms_processed(course):
    """
    Formats terms that a course is offered in appropriately
    """

    results = terms(course)

    if bool(results):
        term = results[0][0]
        lst = ["Autumn", "Winter", "Spring", "Summer"]
        if term in lst:
            return (course + " is offered in " + term + ".")
    elif not bool(notes(course)):
        return ("I'm sorry, I couldn't recognize the course code: " + course + ".")
    else:
        return ("I'm afraid I don't know exactly when " + course + " is offered.")


def is_term_in(course, term):
    """
    fxn that returns True if the input course is offered in the input term,
    False otherwise
    """

    results = terms(course)
    term1 = results[0][0]
    if term == term1:
        return True
    else:
        return False


#---------------------------------------------------------------------Max---------------------------------------------------------------

def majors_available_data():

    with open('scraped_data/major_reqs_data.json') as file:
        major_info = json.load(file)

    majors_available = set()

    for department, majors in major_info.items():
        for major in majors:
            majors_available.add(major)

    return majors_available



def majors_available():
    '''
    Answers which majors the chatbot supports.
    '''

    with open('scraped_data/major_reqs_data.json') as file:
        major_info = json.load(file)

    rv = "I currently support these majors in the following departments:" + "\n"

    for department, majors in major_info.items():
        dept_majors = "    " + department + ":\n"
        for major in majors:
            dept_majors += "        " + major + "\n"
        rv += dept_majors

    return rv

def major_reqs_left_processing(courses_taken, major):
    '''
    courses_taken is a set
    major is a string
    '''

    with open('scraped_data/major_reqs_data.json') as file:
        major_info = json.load(file)

    department = re.search("Statistics|Economics|Mathematics|Physics|Chemistry", major)
    department = department.group()

    major_reqs = major_info[department][major]

    reqs_satisfied = []
    reqs_unsatisfied = []

    for req in major_reqs:

        req_met, satisfier = process_req(courses_taken, req)

        if req_met:
            reqs_satisfied.append(satisfier)
        else:
            reqs_unsatisfied.append(req)

    elec_count = 0
    for item in reqs_unsatisfied:
        if item == "!ELEC":
            elec_count += 1

    return reqs_satisfied, reqs_unsatisfied, elec_count

    
def major_reqs_left_to_text(courses_taken, major):

    reqs_satisfied, reqs_unsatisfied, elec_count = major_reqs_left_processing(courses_taken, major)

    output_text = ("As far as I understand it, you have met %d requirements, and have %d more to go " +
    "of which %d are electives.\nYou should check whether you meet the electives online, " +
    "they're a little too complicated for me to understand.") % (len(reqs_satisfied), len(reqs_unsatisfied), elec_count)

    if reqs_satisfied != []:
        satisfied_text = "\n\nYou have successfully met the following requirement(s):\n"
        for req in reqs_satisfied:
            satisfied_text += ("    " + req_to_text(req) + "\n")
        output_text += satisfied_text[:-1]

    if reqs_unsatisfied != []:
        unsatisfied_text = "\n\nYou have yet to meet the following requirement(s):\n"
        for req in reqs_unsatisfied:
            if req != "!ELEC":
                unsatisfied_text += ("    " + req_to_text(req) + "\n")
        if elec_count > 0:
            unsatisfied_text += ("    " + str(elec_count) + " elective(s)")
        else:
            unsatisfied_text = unsatisfied_text[:-1]
        output_text += unsatisfied_text

    return output_text
    
def meet_course_prereqs_processing(courses_taken, course_code):
    '''
    Determines whether a student has satisfied all the requirements to be able
    to enroll in a course.

    Inputs:
        courses_taken (list): a list of all the courses a student has taken
        course_prereqs (list): a structure of nested lists representing prereqs for a course

    Outputs:
        rv (bool): a boolean that is True if requirements are met and False if not
    '''

    with open('scraped_data/prereqs2_data.json') as file:
        prereqs_info = json.load(file)

    if course_code in prereqs_info:
        prereqs = prereqs_info[course_code]
    else:
        return [], []

    reqs_satisfied = []
    reqs_unsatisfied = []

    for req in prereqs:

        req_met, satisfier = process_req(courses_taken, req)

        if req_met:
            reqs_satisfied.append(satisfier)
        else:
            reqs_unsatisfied.append(req)

    return reqs_satisfied, reqs_unsatisfied

def meet_course_prereqs_text(courses_taken, course_code):

    reqs_satisfied, reqs_unsatisfied = meet_course_prereqs_processing(courses_taken, course_code)

    output_text = ("As far as I understand it, you have met %d requirement(s), and have %d more to go.") % (len(reqs_satisfied), len(reqs_unsatisfied))

    if reqs_satisfied != []:
        satisfied_text = "\n\nYou have successfully met the following requirements:\n"
        for req in reqs_satisfied:
            satisfied_text += ("    " + req_to_text(req) + "\n")
        output_text += satisfied_text[:-1]

    if reqs_unsatisfied != []:
        unsatisfied_text = "\n\nYou have yet to meet the following requirements:\n"
        for req in reqs_unsatisfied:
                unsatisfied_text += ("    " + req_to_text(req) + "\n")
        output_text += unsatisfied_text[:-1]

    warning_text = ("\n\nWARNING - I'm not great at determining prerequisites so if you feel something does not make sense, " +
    "you can ask me for the prerequisite text given in the course catalog for more information.\n" +
    "If you discover an error, please let me know by typing 'Incorrect prerequisites for " + course_code + "' in the box below!")

    return (output_text + warning_text)

def process_req(courses_taken, req):
    '''
    Helper function for major_reqs_left() that determines whether a req
    is met given the courses taken by the student.
    '''

    # If the req is just a string we can search for it in courses_taken.
    if isinstance(req, str):
        if req in courses_taken:
            return (True, req)
    
    # If it's a list we need to check its items.
    elif isinstance(req, list):
        
        # A quick sweep through in case there are any single strings that
        # match.
        for sub_req in req:
            if isinstance(sub_req, str):
                if sub_req in courses_taken:
                    return (True, sub_req)

            elif isinstance(sub_req, list):

                seq_met = True

                # If a single sequence requirement is not satisfied, we know
                # it's not satisfied.
                for seq_req in sub_req:
                    if seq_req not in courses_taken:
                        seq_met = False
                        break

                # If all sequence requirements were met, we know this req
                # was satisfied.
                if seq_met:
                    return (True, sub_req)

    return (False, None)

def req_to_text(req):
    '''
    Helper for major_reqs_left(). Takes a req and makes it human readable.
    '''

    output_text = ""

    if isinstance(req, str):
        output_text += req
    
    elif isinstance(req, list):

        for sub_req in req:
            if isinstance(sub_req, str):
                output_text += (" OR " + sub_req)

            if isinstance(sub_req, list):

                seq_text = ""

                length = len(sub_req)
                for i, seq_req in enumerate(sub_req):
                    if i + 1 < length:
                        seq_text += ", " + seq_req
                    else:
                        seq_text += " AND " + seq_req

                seq_text = seq_text[2:]

                output_text += " OR " + "(" + seq_text + ")"

    output_text = output_text.strip(" OR ")

    return output_text
