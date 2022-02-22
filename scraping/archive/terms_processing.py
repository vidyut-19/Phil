
# Terms Processing

import re

def process_text(terms_text):

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