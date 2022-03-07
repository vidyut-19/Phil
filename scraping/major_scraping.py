
# Scrape Majors

import urllib3
import certifi
import re
import bs4
import json


major_websites = {"Statistics": "http://collegecatalog.uchicago.edu/thecollege/statistics/",
"Economics": "http://collegecatalog.uchicago.edu/thecollege/economics/",
"Mathematics": "http://collegecatalog.uchicago.edu/thecollege/mathematics/",
"Physics": "http://collegecatalog.uchicago.edu/thecollege/physics/",
"Chemistry": "http://collegecatalog.uchicago.edu/thecollege/chemistry/"}

def test():
    with open('major_reqs_data.json') as file:
        data = json.load(file)
    return data

def go():

    major_data = []
    pre_lim_data = []

    major_reqs_dict = {}

    for major, website in major_websites.items():

        count = 0
        
        major_tables = find_tables(website)

        major_reqs = {}

        for major_table in major_tables:
            count += 1
            major_reqs["Major Option: " + str(count)] = major_table

        major_reqs_dict[major] = major_reqs

    with open('major_reqs_data2.json', 'w') as file:
        json.dump(major_reqs_dict, file)


def find_tables(website):

    pm = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    html = pm.urlopen(url=website, method="GET").data
    soup = bs4.BeautifulSoup(html, features="html.parser")

    course_tables = soup.find_all("table", class_="sc_courselist")

    major_tables = []

    major_table = []

    for table_tag in course_tables:

        table_title = table_tag.find("span", class_="courselistcomment")
        if table_title:
            table_title_text = table_title.text

            if re.search("GENERAL EDUCATION", table_title_text):
                major_table = analyze_table(table_tag)

            elif re.search("MAJOR", table_title_text):
                major_table += analyze_table(table_tag)
                major_tables.append(major_table)
                major_table = []

    return major_tables

def analyze_table(table):

    rows = table.find_all("tr")

    is_indented = False
    times_to_add = 1
    courses_to_add = []

    major_output = []

    for row in rows:

        row_text = row.text
        row_text = row_text.replace("\xa0", " ")
        # Determines whether certain classes are substitutes
        if row.find("div", style="margin-left: 20px;") or re.search("^or ", row_text):
            is_indented = True

        else:
            is_indented = False

            # If there's no indentation, we can add the last queue of courses to the major
            if courses_to_add != []:
                for i in range(times_to_add):
                    major_output.append(courses_to_add)
            times_to_add = 1
            courses_to_add = []

        times_to_add = calc_times_to_add(row_text)

        # Determines whether we have received an elective text like "One Perspectives elective"
        elective = re.search("[eE]lective", row_text)

        if elective and not re.search(":", row_text):
            electives = add_electives(row_text)
            major_output += electives

        # If we have no electives, add the course codes in the row to the queue
        else:

            req_courses = re.findall("(?:[A-Z]{4} [0-9]{5}(?:/[0-9]{5})*(?:/[A-Z]{4} [0-9]{5})*)|(?:[0-9]{5})", row_text)

            # Cleans up courses given in abbreviated form such as "ECON 20000-20100-20200" and "MATH 16110 & 16210"
            req_courses = clean_courses(req_courses)

            # Prevents single nested lists
            if len(req_courses) == 1:
                courses_to_add += req_courses
            elif len(req_courses) >= 1:
                courses_to_add.append(req_courses)

    return major_output
    
def calc_times_to_add(row_text):
    
    mult_times = re.search("^Two|Three|Four|Five|Six|Seven|Eight|Nine", row_text)

    if mult_times:
        mult_times = mult_times.group()
        
        spell_nums = {"Two": 2, "Three": 3, "Four": 4, "Five": 5,
        "Six": 6, "Seven": 7, "Eight": 8, "Nine": 9}

        times_to_add = spell_nums[mult_times]

        return times_to_add

    else:
        return 1

def add_electives(row_text):

    num_electives = re.search("[0-9]00", row_text)
    num_electives = num_electives.group()
    num_electives = int(num_electives)
    num_electives /= 100
    num_electives = int(num_electives)

    electives = []
    for i in range(num_electives):
        electives += ["!ELEC"]

    #print(electives)

    return electives

def clean_courses(courses):

    print(courses)

    for i, course in enumerate(courses):

        if re.findall('[A-Z]{4}', course) == []:
            courses[i] = courses[i-1][:4] + " " + course
                    
        if re.findall('/|-', course) != []:
            fixed_courses = []
            depts = re.findall('[A-Z]{4}', course)
            numbers = re.findall('[0-9]{5}', course)

            if len(depts) == 1:
                for number in numbers:
                    fixed_courses.append([depts[0] + ' ' + number])

            else:
                for j, dept in enumerate(depts):
                    fixed_courses.append([dept + ' ' + numbers[j]])
            print(fixed_courses)
            courses[i] = fixed_courses
    print(courses)
    return courses
