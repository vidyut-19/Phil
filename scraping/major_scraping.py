
# Scrape Majors

import urllib3
import certifi
import re
import bs4

'''
To Do:

mark with special thing if there is a sentence explaining a course

store how many credits the major is

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

def go():

    count = 0

    major_data = []
    pre_lim_data = []

    for website in websites_to_visit:
        
        major_tables = find_tables(website)

        for table in major_tables:

            pre_lim_data.append(analyze_table(table))

        for i in range(len(pre_lim_data)):
            if i % 2 != 0:
                complete_major = pre_lim_data[i-1] + pre_lim_data[i]
                major_data.append(complete_major)
            else:
                pass

        for major in major_data:
            print(major)
            count += 1
            print("---------------------------------------")
        print(count)


def find_tables(website):

    pm = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    html = pm.urlopen(url=website, method="GET").data
    soup = bs4.BeautifulSoup(html, features="html.parser")

    course_tables = soup.find_all("table", class_="sc_courselist")

    major_tables = []

    for table_tag in course_tables:

        table_title = table_tag.find("span", class_="courselistcomment")
        if table_title:
            table_title_text = table_title.text

            if re.search("GENERAL EDUCATION|MAJOR", table_title_text):
                major_tables.append(table_tag)

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

    for i, course in enumerate(courses):

        if re.findall('[A-Z]{4}', course) == []:
            courses[i] = courses[i-1][:4] + " " + course
                    
        if re.findall('/|-', course) != []:
            fixed_courses = []
            depts = re.findall('[A-Z]{4}', course)
            numbers = re.findall('[0-9]{5}', course)

            if len(depts) == 1:
                for number in numbers:
                    fixed_courses.append(depts[0] + ' ' + number)

            else:
                for j, dept in enumerate(depts):
                    fixed_courses.append(dept + ' ' + numbers[j])

            courses[i] = fixed_courses

    return courses