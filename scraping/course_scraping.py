
import re
import bs4
import sys
import csv
import process
import pa2util

# import prereqs_processing
# import instructors_processing
# import terms_processing

def go(instructors_csv=None, terms_csv=None, prereqs_csv=None, notes_csv=None, equivalent_csv=None):

    starting_url = ("http://www.classes.cs.uchicago.edu/archive/2015/winter"
                    "/12200-1/new.collegecatalog.uchicago.edu/index.html")
    limiting_domain = "classes.cs.uchicago.edu"

    # Initializes variables related to visiting websites systematically
    queue = [starting_url]
    visited_links = [starting_url]
    count = 0

    # Initializes lists containing scraped information
    instructors_info = []
    terms_info = []
    prereqs_info = []
    notes_info = []
    equivalent_info = []

    all_info = [instructors_info, terms_info, prereqs_info, notes_info, equivalent_info]

    while len(queue) > 0 and count < 1000:
        analyze_link(queue[0], limiting_domain, visited_links, queue, all_info)
        count += 1

    csv_info_dict = {instructors_csv: instructors_info, terms_csv: terms_info,
    prereqs_csv: prereqs_info, notes_csv: notes_info, equivalent_csv: equivalent_info}

    create_csvs(csv_info_dict, all_info)

def analyze_link(url, limiting_domain, visited_links, queue, all_info):

    # Loads in the url and creates the soup object.
    request = pa2util.get_request(url)
    assert request != None, "pa2util.get_request(url) returned None"
    url = pa2util.get_request_url(request)
    html_text = pa2util.read_request(request)
    assert html_text != None, "pa2util.read_request(request) returned None"
    soup = bs4.BeautifulSoup(html_text, features="html.parser")
 
    scrape_info(soup, all_info)

    # Calls find_links() to add any of the unvisited links on this page to the queue.
    find_links(soup, url, limiting_domain, visited_links, queue)

    # Deletes the current url from the front of the queue because we are done with it.
    del queue[0]

def scrape_info(soup, all_info):

    courses = soup.find_all('div', class_="courseblock main")

    for course in courses:
        subsequences = find_sequence(course) 
           
        if subsequences == []:
            pull_information(course, all_info)

        else:
            for subsequence in subsequences:
                pull_information(subsequence, all_info)

def pull_information(course, all_info):

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
    terms_text, terms_data = pull_terms(detail_text)
    prereqs_text, prereqs_data = pull_prereqs(detail_text)
    notes_text = pull_notes(detail_text)
    equivalent_text, equivalent_data = pull_equivalent(detail_text)

    # Appending the information we have found to the lists----------------

    all_info[0].append((course_code, instructors_text, instructors_data))
    all_info[1].append((course_code, terms_text, terms_data))
    all_info[2].append((course_code, prereqs_text, prereqs_data))
    all_info[3].append((course_code, notes_text))
    all_info[4].append((course_code, equivalent_text, equivalent_data))

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

def create_csvs(csv_info_dict, all_info):

    for csv_to_create, csv_info in csv_info_dict.items():
        if csv_to_create != None:

            if csv_info in (all_info[0], all_info[1], all_info[4]):

                with open(csv_to_create + "_data.csv", "w") as file:

                    writer = csv.writer(file, delimiter=',')

                    for course_code, _, course_data in csv_info:
                        for datum in course_data:
                            writer.writerow([course_code, datum])

                with open(csv_to_create + "_text.csv", "w") as file:

                    writer = csv.writer(file, delimiter=',')

                    for course_code, course_text, _ in csv_info:
                            writer.writerow([course_code, course_text])

            elif csv_info == all_info[3]:

                with open(csv_to_create + "_text.csv", "w") as file:

                    writer = csv.writer(file, delimiter=',')

                    for course_code, course_text in csv_info:
                            writer.writerow([course_code, course_text])

            elif csv_info == all_info[2]:
                pass


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
        prereqs_data = process.prereqs(prereqs_text)
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