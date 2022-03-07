
# The code that answers task requests

import sqlite3
import os
import json
import re
            
'''
To Do

working with _text.csv files
- fxn that returns prereq text
- fxn that returns notes text
- fxn that returns equivalents text
- fxn that returns terms offred text
- fxn that returns an instructors email

working with _data.csv files
- fxn that confirms whether a course is offered in a certain term
- fxn that confirms whether a course is an equivalent for another
- fxn that returns the full names of the professors teaching

'''

# Return prereq text or null substitute
def prerequisites(course):
    """
    What are the prerequisites for this course?
    COMPLETE THIS NOW THAT MAJOR SCRAPING IS DONE
    """

    connection = sqlite3.connect("scraping/scraped_data/data.db")
    c = connection.cursor()
    query = "SELECT x \nFROM x \n JOIN x \nWHERE "
    params = (course,)
    r = c.execute(query, params)

    return r.fetchall()

def professors(course):
    """
    Which Professor is teaching this course?
    """

    connection = sqlite3.connect("scraping/scraped_data/data.db")
    c = connection.cursor()
    query = "SELECT id2.professor_name, ie.professor_email, ifn.professor_full_name\nFROM ins_data2 as id2\nJOIN instructor_emails as ie ON id2.professor_name = ie.professor_name\nJOIN instructors_full_names as ifn on ifn.professor_name = id2.professor_name\nWHERE id2.course = ?" 
    params = (course,)
    r = c.execute(query, params)
    
    results = r.fetchall()

    if not bool(results):
        return "Couldn't find professor info for that course"
    else:
        if len(results) == 1:
            if bool(full_name) and name != "Unkown" and email != "UNKNOWN":
                return "The professor teaching this course is {}, you can reach them at {}".format(full_name, email)
            else:
                return "The professor teaching this course is {}, you can reach them at {}".format(name, email)
        else:
            return "check this edge case"


def equivalent(course):
    """
    What are equivalent courses to this course?
    """

    connection = sqlite3.connect("scraping/scraped_data/data.db")
    c = connection.cursor()
    query = "SELECT equivalent_course\nFROM equivalent_data\nWHERE course = ?" 
    params = (course,)
    r = c.execute(query, params)

    string = "The equivalent courses to " + course + " are: "
    fixed = [course[0] for course in r]
    string += ", ".join(fixed)

    return string


def notes(course):
    """
    What are necessary notes for this course?
    """

    connection = sqlite3.connect("scraping/scraped_data/data.db")
    c = connection.cursor()
    query = "SELECT note\nFROM notes_text\nWHERE course = ?" 
    params = (course,)
    r = c.execute(query, params)
    results = r.fetchall()

    if bool(results[0][0]):
        return "Here's something you should know about this class: " + results[0][0].strip()
    

def terms(course):
    """
    When is this course offered?
    """

    connection = sqlite3.connect("scraping/scraped_data/data.db")
    c = connection.cursor()
    query = "SELECT term\nFROM terms_text\nWHERE course = ?" 
    params = (course,)
    r = c.execute(query, params)
 
    results = r.fetchall()

    fixed = [term[0].strip() for term in results]
    text = ", ".join(fixed)

    if bool(results):
        return "This course is offered in the following term(s): " + text

#---------------------------------------------------------------------Max---------------------------------------------------------------

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

def major_reqs_left(courses_taken, major):
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
    
def meet_course_prereqs(courses_taken, course_code):
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
        return "This course has no prerequisites so you already meet them all!"

    reqs_satisfied = []
    reqs_unsatisfied = []

    for req in prereqs:

        req_met, satisfier = process_req(courses_taken, req)

        if req_met:
            reqs_satisfied.append(satisfier)
        else:
            reqs_unsatisfied.append(req)

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
