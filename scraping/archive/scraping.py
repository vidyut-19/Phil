

'''
To Do

write outputs of fxn to a csv file

combine processing supplementary files into one file

'''


# Functions to scrape database data

import urllib3
import certifi
import re
import bs4
import prereqs_processing
import instructors_processing
import terms_processing
import csv

'''
UChicago Top 10 Majors:
1. Economics 2. Biological Sciences 3. Mathematics 4. Political Science 5. Public Policy Studies
6. Computer Science 7. Physics 8. Psychology 9. English 10. History
'''

websites_to_visit = ["http://collegecatalog.uchicago.edu/thecollege/economics/",
"http://collegecatalog.uchicago.edu/thecollege/biologicalsciences/",
"http://collegecatalog.uchicago.edu/thecollege/mathematics/",
"http://collegecatalog.uchicago.edu/thecollege/politicalscience/",
"http://collegecatalog.uchicago.edu/thecollege/publicpolicystudies/",
"http://collegecatalog.uchicago.edu/thecollege/computerscience/",
"http://collegecatalog.uchicago.edu/thecollege/physics/",
"http://collegecatalog.uchicago.edu/thecollege/psychology/",
"http://collegecatalog.uchicago.edu/thecollege/englishlanguageliterature/",
"http://collegecatalog.uchicago.edu/thecollege/history/"]

instructors_info = []
terms_info = []
prereqs_info = []
notes_info = []
equivalent_info = []

def go(instructors_csv=None, terms_csv=None, prereqs_csv=None, notes_csv=None, equivalent_csv=None):

    for website in websites_to_visit:
        analyze_link(website)

    create_csvs([instructors_csv, terms_csv, prereqs_csv, notes_csv, equivalent_csv])


def analyze_link(website):

    # Loads in the url and creates the soup object.
    pm = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    html = pm.urlopen(url=website, method="GET").data
    soup = bs4.BeautifulSoup(html, features="html.parser")

    courses = soup.find_all('div', class_="courseblock main")

    for course in courses:

        subsequences = find_sequence(course)    

        if subsequences == []:

            analyze_course(course)

        else:

            for subsequence in subsequences:

                analyze_course(subsequence)

def analyze_course(course):

    instructors_tup, terms_tup, prereqs_tup, notes_tup, equivalent_tup = pull_information(course)

    instructors_info.append(instructors_tup)
    terms_info.append(terms_tup)
    prereqs_info.append(prereqs_tup)
    notes_info.append(notes_tup)
    equivalent_info.append(equivalent_tup)
        

def pull_information(course):

    # Title Related Things------------------------------------------------

    title_tag = course.find_all('p', class_="courseblocktitle")
    title_text = title_tag[0].text

    title = re.search(r'\. .*\.|\) ', title_text)
    title = title.group()
    title = title.strip(' .')

    course_code = re.search(r'[A-Z]{4}\xa0[0-9]{5}', title_text)
    course_code = course_code.group()
    course_code = course_code.replace("\xa0", " ")

    units = re.search(r'[0-9]+ Units', title_text)
    units = units.group()

    # Body Related Things-------------------------------------------------

    course_block_detail = course.find_all('p', class_="courseblockdetail")
    detail_text = course_block_detail[0].text

    instructors_text, instructors_data = pull_instructors(detail_text)
    terms_text, terms_data = pull_terms(detail_text)
    prereqs_text, prereqs_data = pull_prereqs(detail_text)
    notes_text = pull_notes(detail_text)
    equivalent_text, equivalent_data = pull_equivalent(detail_text)

    return ((course_code, instructors_text, instructors_data),
    (course_code, terms_text, terms_data),
    (course_code, prereqs_text, prereqs_data),
    (course_code, notes_text),
    (course_code, equivalent_text, equivalent_data))



def create_csvs(csvs_to_create):

    # could make a dictionary with csv_to_create and list of info in it, then iterate through that

    for i, csv_to_create in enumerate(csvs_to_create):
        if csv_to_create != None:

            if i in [0, 1, 4]:

            with open(instructors_csv + "_data.csv", 'w') as file:
                writer = csv.writer(file, delimiter=',')

                for course_code, _, course_data in instructors_info:
                    for datum in course_data:
                        writer.writerow([course_code, datum])

            with open(instructors_csv + "_text.csv", 'w') as file:
                writer = csv.writer(file, delimiter=',')

                for course_code, course_text, _ in instructors_info:
                        writer.writerow([course_code, course_text])

    if terms_csv:

        with open(terms_csv + "_data.csv", 'w') as file:
            writer = csv.writer(file, delimiter=',')

            for course_code, _, course_data in terms_info:
                for datum in course_data:
                    writer.writerow([course_code, datum])

        with open(terms_csv + "_text.csv", 'w') as file:
            writer = csv.writer(file, delimiter=',')

            for course_code, course_text, _ in terms_info:
                    writer.writerow([course_code, course_text])

#HELPERS------------------------------------------------------------------------------------------

def pull_instructors(detail_text):

    instructors_bloc = re.search(r'(?<=Instructor\(s\): ).*(?=Terms Offered)', detail_text)

    if instructors_bloc:
        instructors_text = instructors_bloc.group()
        instructors_data = instructors_processing.process_text(instructors_text)
    else:
        instructors_text = "Unknown"
        instructors_data = ["Unknown"]

    instructors_text = instructors_text.replace("\xa0", "")

    return (instructors_text, instructors_data)

def pull_terms(detail_text):

    terms_bloc = re.search(r'(?<=Terms Offered: )(?:[a-zA-Z0-9-\.]*\s)+', detail_text)

    if terms_bloc:
        terms_text = terms_bloc.group()
        terms_text = terms_text.replace("\n", " ")
        terms_text = terms_text.replace("Equivalent", "")
        terms_data = terms_processing.process_text(terms_text)
    else:
        terms_text = "Unknown"
        terms_data = ["Unknown"]

    return (terms_text, terms_data)

def pull_prereqs(detail_text):

    prereqs_bloc = re.search(r'(?<=Prerequisite\(s\): ).*\n', detail_text)

    if prereqs_bloc:
        prereqs_text = prereqs_bloc.group()
        prereqs_data = prereqs_processing.process_text(prereqs_text)
    else:
        prereqs_text = ""
        prereqs_data = []

    return (prereqs_text, prereqs_data)

def pull_notes(detail_text):

    notes_bloc = re.search(r'(?<=Note\(s\): ).*\n', detail_text)

    if notes_bloc:
        notes_text = notes_bloc.group()
    else:
        notes_text = ""

    return notes_text

def pull_equivalent(detail_text):

    equivalent_bloc = re.search(r'(?<=Equivalent Course\(s\): ).*\n', detail_text)

    if equivalent_bloc:
        equivalent_text = equivalent_bloc.group()
        equivalent_data = re.findall('[a-zA-Z]{4} [0-9]{5}', equivalent_text)
    else:
        equivalent_text = ""
        equivalent_data = []

    return (equivalent_text, equivalent_data)

#Provided by PA2--------------------------------------------------------------------------------

def is_subsequence(tag):
    '''
    Does the tag represent a subsequence?
    '''
    return isinstance(tag, bs4.element.Tag) and 'class' in tag.attrs \
        and tag['class'] == ['courseblock', 'subsequence']


def is_whitespace(tag):
    '''
    Does the tag represent whitespace?
    '''
    return isinstance(tag, bs4.element.NavigableString) and (tag.strip() == "")


def find_sequence(tag):
    '''
    If tag is the header for a sequence, then
    find the tags for the courses in the sequence.
    '''
    rv = []
    sib_tag = tag.next_sibling
    while is_subsequence(sib_tag) or is_whitespace(tag):
        if not is_whitespace(tag):
            rv.append(sib_tag)
        sib_tag = sib_tag.next_sibling
    return rv