
import re
import bs4
import sys
import csv
import process
import pa2util
import json

def go(instructors_file=None, terms_file=None, prereqs_file=None, prereqs_json=None, notes_file=None, equivalent_file=None):

    max_counts = {"ins_count": 0, "terms_count": 0, "prereqs_count": 0, "notes_count": 0, "equi_count": 0}

    starting_url = ("http://www.classes.cs.uchicago.edu/archive/2015/winter"
                    "/12200-1/new.collegecatalog.uchicago.edu/index.html")
    limiting_domain = "classes.cs.uchicago.edu"

    # Initializes variables related to visiting websites systematically
    queue = [starting_url]
    visited_links = [starting_url]
    count = 0

    all_info = {"instructors_lst": [], "terms_lst": [], "prereqs_lst": [], "prereqs_dict": {}, "notes_lst": [], "equivalent_lst": []}

    while len(queue) > 0 and count < 1000:
        analyze_link(queue[0], limiting_domain, visited_links, queue, all_info, max_counts)
        count += 1

    file_info_dict = {instructors_file: all_info["instructors_lst"], terms_file: all_info["terms_lst"],
    prereqs_file: all_info["prereqs_lst"], prereqs_json: all_info["prereqs_dict"], notes_file: all_info["notes_lst"],
    equivalent_file: all_info["equivalent_lst"]}

    create_files(file_info_dict, all_info)

def analyze_link(url, limiting_domain, visited_links, queue, all_info, max_counts):

    # Loads in the url and creates the soup object.
    request = pa2util.get_request(url)
    assert request != None, "pa2util.get_request(url) returned None"
    url = pa2util.get_request_url(request)
    html_text = pa2util.read_request(request)
    assert html_text != None, "pa2util.read_request(request) returned None"
    soup = bs4.BeautifulSoup(html_text, features="html.parser")
 
    scrape_info(soup, all_info, max_counts)

    # Calls find_links() to add any of the unvisited links on this page to the queue.
    find_links(soup, url, limiting_domain, visited_links, queue)

    # Deletes the current url from the front of the queue because we are done with it.
    del queue[0]

def scrape_info(soup, all_info, max_counts):

    courses = soup.find_all('div', class_="courseblock main")

    for course in courses:
        subsequences = find_sequence(course) 
           
        if subsequences == []:
            pull_information(course, all_info, max_counts)

        else:
            for subsequence in subsequences:
                pull_information(subsequence, all_info, max_counts)

def pull_information(course, all_info, max_counts):

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
    if units:
        units = units.group()
    else:
        units = "UNKNOWN"

    # Body Related Things-------------------------------------------------

    course_block_detail = course.find_all('p', class_="courseblockdetail")
    detail_text = course_block_detail[0].text

    instructors_text, instructors_data = pull_instructors(detail_text)
    all_info["instructors_lst"].append((course_code, instructors_text, instructors_data))

    if len(instructors_text) > max_counts["ins_count"]:
        max_counts["ins_count"] = len(instructors_text)

    terms_text, terms_data = pull_terms(detail_text)
    all_info["terms_lst"].append((course_code, terms_text, terms_data))
    if len(terms_text) > max_counts["terms_count"]:
        max_counts["terms_count"] = len(terms_text)

    prereqs_text, prereqs_data = pull_prereqs(detail_text)
    all_info["prereqs_lst"].append((course_code, prereqs_text))
    if prereqs_data not in [[], [[]]]:
        all_info["prereqs_dict"][course_code] = prereqs_data
    if len(prereqs_text) > max_counts["prereqs_count"]:
        max_counts["prereqs_count"] = len(prereqs_text)

    notes_text = pull_notes(detail_text)
    all_info["notes_lst"].append((course_code, notes_text))
    if len(notes_text) > max_counts["notes_count"]:
        max_counts["notes_count"] = len(notes_text)

    equivalent_text, equivalent_data = pull_equivalent(detail_text)        
    all_info["equivalent_lst"].append((course_code, equivalent_text, equivalent_data))
    if len(equivalent_text) > max_counts["equi_count"]:
        max_counts["equi_count"] = len(equivalent_text)

def find_links(soup, url, limiting_domain, visited_links, queue):
    '''
    Given a soup object, this function finds all links in url's html
    that we are interested in. It adds these to the queue and our
    visited links.

    Inputs:
        soup (soup): soup object representing the html found on the website
        url (str): the url we are currently looking for links on
        limiting_domain (str): the limiting domain
        visited_links (lst): a list storing all urls that have been analyzed
        queue (lst): list of all the urls that still need to be visited
    '''

    link_tags = soup.find_all("a")

    for link_tag in link_tags:

        if link_tag.has_attr("href"):
            link = link_tag["href"]

            # Formats links into absolute urls.
            if not pa2util.is_absolute_url(link):
                link = pa2util.remove_fragment(link)
                link = pa2util.convert_if_relative_url(url, link)

            # If the link is okay to follow, add it to the queue
            if link not in visited_links:
                if pa2util.is_url_ok_to_follow(link, limiting_domain):
                    # For some reason is_url_ok would return true for archived links.
                    if "archives" not in link:

                        queue.append(link)
                        visited_links.append(link)

def create_files(file_info_dict, all_info):

    for file_to_create, file_info in file_info_dict.items():
        if file_to_create != None:
            print(file_to_create)

            if file_info in (all_info["instructors_lst"], all_info["terms_lst"], all_info["equivalent_lst"]):

                with open(file_to_create + "_data.csv", "w") as file:

                    writer = csv.writer(file, delimiter=',')

                    for course_code, _, course_data in file_info:
                        for datum in course_data:
                            writer.writerow([course_code, datum])

                with open(file_to_create + "_text.csv", "w") as file:

                    writer = csv.writer(file, delimiter=',')

                    for course_code, course_text, _ in file_info:
                            writer.writerow([course_code, course_text])

            elif file_info == all_info["notes_lst"]:

                with open(file_to_create + "_text.csv", "w") as file:

                    writer = csv.writer(file, delimiter=',')

                    for course_code, course_text in file_info:
                            writer.writerow([course_code, course_text])

            elif file_info == all_info["prereqs_lst"]:

                with open(file_to_create + "_text.csv", "w") as file:

                    writer = csv.writer(file, delimiter=',')

                    for course_code, course_text in file_info:
                            writer.writerow([course_code, course_text])

            elif file_info == all_info["prereqs_dict"]:

                with open(file_to_create + '_data.json', 'w') as file:
                    json.dump(all_info["prereqs_dict"], file)


#HELPERS------------------------------------------------------------------------------------------

def pull_instructors(detail_text):

    instructors_bloc = re.search(r'(?<=Instructor\(s\): ).*(?=Terms Offered)', detail_text)

    if instructors_bloc:
        instructors_text = instructors_bloc.group()
        instructors_data = process.instructors(instructors_text)
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
        terms_data = process.terms(terms_text)
    else:
        terms_text = "Unknown"
        terms_data = ["Unknown"]

    return (terms_text, terms_data)

def pull_prereqs(detail_text):

    prereqs_bloc = re.search(r'(?<=Prerequisite\(s\): ).*\n', detail_text)

    if prereqs_bloc:
        prereqs_text = prereqs_bloc.group()
        prereqs_text = prereqs_text.strip("\n")
        prereqs_data = process.prereqs(prereqs_text)
    else:
        prereqs_text = "!NONE"
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