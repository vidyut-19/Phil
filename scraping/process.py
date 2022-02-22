
# Processing Functions

import re

def instructors(instructor_text):

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

def terms(terms_text):

    if re.search("TBD", terms_text):
        return ["Unknown"]

    terms_data = re.findall('Autumn|Fall|Winter|Spring|Summer|autumn|fall|winter|spring|summer', terms_text)

    if terms_data == []:
        terms_data = ["Unknown"]

    output = []

    for term in terms_data:
        if term not in output:
            output.append(term)

    return output

def prereqs(prereq_text):
    '''
    Takes the prereq_text and processes it in a way that the
    computer can logically handle.

    Inputs:
        prereq_text (str): text from the course catalog that
        says what the prerequisites for a course are
    '''

    processed_txt = [prereq_text]

    # Splits by ;
    if re.findall(';', prereq_text) != []:
        processed_txt = prereq_text.split(";")

    # Splits into sentences
    for i, phrase in enumerate(processed_txt):

        phrase = phrase.strip(".")

        if re.findall('\.', phrase) != []:

            sentences = phrase.split(".")

            # Splits sentences by and's
            for j, sentence in enumerate(sentences):
                if re.findall(' and | AND ', sentence) != []:
                    and_splits = re.split(' and | AND ', sentence)
                    sentences[j] = and_splits

            processed_txt[i] = sentences

        # If there are no periods, we still want to split up ands
        if re.findall(' and | AND ', phrase) != []:
            and_splits = re.split(' and | AND ', phrase)
            processed_txt[i] = and_splits

    # Calls the obtain_prereqs helper on each parcel of info
    output = recursion(processed_txt)

    # Removes nested loops that are artificats from selection process
    #clean_output = clean(output)

    return output #clean_output

def recursion(text_inputs):

    output = []

    for item in text_inputs:

        # Base Case
        if type(item) != list:

            set_courses = obtain_prereqs(item)
            if set_courses != []:
                output.append(set_courses)

        # Recrusive Case
        else:
            output.append(recursion(item))

    return output

def clean(output):
    # Source: stackoverflow.com/questions/26619381/clean-nested-lists-in-python
    if isinstance(output, list):
        if len(output) == 1:
            return clean(output[0])
        return [clean(i) for i in output]
    return output
            
def obtain_prereqs(item):
    '''
    Takes a logic parcel and makes sense of it using regular expressions

    Inputs:
        item (str): string with courses that should all be substitutes

    Outputs:
        courses_and_numbers (lst): list of all the substitutes in a parcel
    '''

    courses_and_numbers = re.findall('(?:[a-zA-Z]{4} [0-9]{5}(?:/[0-9]{5})*(?:/[a-zA-Z]{4} [0-9]{5})*)|(?:[0-9]{5})', item)

    # Cleans up courses that only had a number given by assigning them the most recent dept
    for i, course in enumerate(courses_and_numbers):

        # Cleans up courses that only had a number given by assigning them the most recent dept
        if re.findall('[a-zA-Z]{4}', course) == []:
            courses_and_numbers[i] = courses_and_numbers[i-1][:4] + " " + course

        # If we find courses seperated by /, break them up into equivs
        if re.findall('/', course) != []:

            fixed_courses = []

            depts = re.findall('[a-zA-Z]{4}', course)

            numbers = re.findall('[0-9]{5}', course)

            if len(depts) == 1:
                for number in numbers:
                    fixed_courses.append(depts[0] + ' ' + number)

            else:
                for j, dept in enumerate(depts):
                    fixed_courses.append(dept + ' ' + numbers[j])

            courses_and_numbers[i] = fixed_courses

    return courses_and_numbers