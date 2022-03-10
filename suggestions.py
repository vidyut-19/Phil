# Winter '22 - CS122 Group Project - [insert group name here]

# Code for mapping uninterpretable questions to preset questions [DRAFT]

# Omar Khan, Vidyut Baradwaj, Max Huisman

import sqlite3
import os

#Q1 = "What are the " + course.prerequisites + " for this course?"
q1map = ["prerequisite", "prerequisites", "prereq", "req", "required", "requirements", "need", "sequence", "sequences"]

#Q2 = "Does " + course.full_string + " count as an elective for" + program
q2map = ["elective", "count"]

#Q3 = "How are the " + course.prof + "'s reviews?"
q3map = ["difficulty", "hours", "work", "hard", "easy"]

#Q4 = "What are equivalent courses to " course + "?"
q4map = ["equivalent", "cross-listed", "cross", "listed", "listing", "cross listed", "equal"]

#Q5 = "Which professors are teaching this course?"
q5map = ["professor", "prof", "instructor", "teach", "teaching"]

def score(question):
    """
    APPARENTLY YOU ARE DOING SOMETHING MUCH BETTER THAN THIS MAX SO 
    FORGET THIS FUNCTION
    """
    questions = [q1, q2, q3, q4, q5, q6, q7, q8, q9, q10]
    maps = [
        q1map, q2map, q3map, q4map, q5map, q6map, q7map, q8map, q9map, q10map
        ]

    best_count = 0
    best_q = []

    for i, m in enumerate(maps):
        count = 0
        for word in question.split():
            if word in m:
                count+=1
        if count >= best_count:
            best_count = count
            best_q.append(questions[i])
    
    if len(best_q) == 1:
        return "Hmm... Sorry, I couldn't quite understand that. I could help you with this instead! {}".format(best_q[0])
    else:
        string = ""
        for q in best_q:
            string += q + "\n"
        return "Hmm... Sorry, I couldn't quite understand that. I could help you with any of these instead!\n" + string
            

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
        return "This course is offered in the following terms: " + text

def get_class_info(course):
    """
    retrieve information for constructing course object with info regarding
    instructor, semesters offered, prereqs
    """
    connection = sqlite3.connect("scraping/scraped_data/data.db")
    c = connection.cursor()
    query = "SELECT term\nFROM terms_text\nWHERE course = ?" 
    params = (course,)
    r = c.execute(query, params)
 
    results = r.fetchall()
