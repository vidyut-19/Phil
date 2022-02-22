
# Tries to update abbreviated names using https://directory.uchicago.edu/ and tries
# to find an email for each instructor

import csv
import urllib3
import certifi
import re
import bs4

def go(instructors_csv, instructors_full_csv_name, email_csv_name):

    unique_instructors = set()

    email_prof_tuples = []

    count = 0

    with open(instructors_csv, "r") as file:

        csv_reader = csv.reader(file)

        for row in csv_reader:

            _, instructor = row

            if instructor not in unique_instructors:

                unique_instructors.add(instructor)

    for instructor in unique_instructors:

        info_tup = instructor_info(instructor)

        email_prof_tuples.append((instructor, info_tup))

        count += 1

        print(count)

    write_csvs(email_prof_tuples, instructors_full_csv_name, email_csv_name)


def write_csvs(email_prof_tuples, instructors_full_csv_name, email_csv_name):

    with open(instructors_full_csv_name + "_full_names.csv", "w") as file:

        writer = csv.writer(file, delimiter=',')

        for instructor, info_tup in email_prof_tuples:

            full_name, _ = info_tup

            writer.writerow([instructor, full_name])

    with open(email_csv_name + "_emails.csv", "w") as file:

        writer = csv.writer(file, delimiter=',')

        for instructor, info_tup in email_prof_tuples:

            _, email = info_tup

            writer.writerow([instructor, email])


def instructor_info(instructor):

    last_name = re.search("[a-zA-Z']+$", instructor)
    last_name = last_name.group()

    instructor_initials = re.findall("^[A-Za-z]| [a-zA-Z]", instructor)
    instructor_initials = "".join(instructor_initials)

    directory_url = "https://directory.uchicago.edu/individuals/results?utf8=&name=" + last_name + "&organization=&cnetid="

    pm = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    html = pm.urlopen(url=directory_url, method="GET").data
    soup = bs4.BeautifulSoup(html, features="html.parser")

    table = soup.find("tbody")

    matches = []

    if table:

        people = table.find_all("tr")

        for person in people:

            text = person.text
            text = text.strip()

            full_name = re.search("^[a-zA-Z']+ [a-zA-Z.']* *[a-zA-Z']+", text)
            if full_name:
                full_name = full_name.group()
            else:
                full_name = instructor             

            email = re.search("[\w]+@uchicago.edu", text)
            if email:
                email = email.group()
            else:
                email = "UNKNOWN"

            full_name_initials = re.findall("^[A-Za-z]| [a-zA-Z]", full_name)
            full_name_initials = "".join(full_name_initials)

            if len(full_name_initials) == 3:
                if instructor_initials == full_name_initials:
                    matches.append((full_name, email))

            elif len(full_name_initials) > 3 and len(instructor_initials) == 3:
                if instructor_initials[0] == full_name_initials[0] and instructor_initials[2] == full_name_initials[-1]:
                    matches.append((full_name, email))

            elif full_name_initials == instructor_initials:
                matches.append((full_name, email))

    if len(matches) == 1:

        return(matches[0])

    else:

        return(instructor, "UNKNOWN")



        
    

