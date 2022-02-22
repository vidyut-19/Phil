
# Processes Instructors

import re

def process_text(instructor_text):

    is_staff = re.search("Staff", instructor_text)
    if is_staff:
        return ["Unknown"]

    is_TBD = re.search("TBD", instructor_text)
    if is_TBD:
        return ["Unknown"]

    instructors = []

    instructor_text = instructor_text.replace(" and", ",")

    # Removes professor tag for pretentious people ;)
    instructor_text = instructor_text.replace("Professor ", "")

    # Handles instructor_text like: A. Sanderson; J. List

    if re.search("^[A-Z]\.", instructor_text):

        trunk_names = re.findall("[A-Z]\. [a-zA-Z']+", instructor_text)

        return trunk_names

    # Handles instructor_text like: Shaikh, Sabina

    elif re.search("^[a-zA-Z']+,", instructor_text):

        reversed_names = re.findall("[a-zA-Z']+, [a-zA-Z']+", instructor_text)

        ordered_names = []

        for rev_name in reversed_names:

            name = rev_name.split(", ")
            name = name[1] + " " + name[0]

            ordered_names.append(name)

        return ordered_names
            
    # Handles instructor_text like: Sabina Shaikh

    elif re.search("^[a-zA-Z']+ (?:[A-Z]\. )*[a-zA-Z']+", instructor_text):

        full_names = re.findall("[a-zA-Z']+ (?:[A-Z]\.* )*[a-zA-Z']+", instructor_text)

        return full_names

    else:

        return ["Unknown"]