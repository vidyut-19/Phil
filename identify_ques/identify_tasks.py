
# Better code to identify questions

import math
import re
import json
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

class Identifier:
    '''
    A model that uses tf idf scores to determine what a user is most
    likely requesting by drawing on a json file filled with previous
    requests.

    Supported tasks:
        What are the prerequisites for this course?
        Who are the instructors for this course?
        What are the equivalent courses for this course?
        Are these courses equivalent?
        What are the notes for this course?
        Which quarters is this course offered?
        What majors do you support?
        What requirements do I have left for my major?
        Do I meet the prerequisites for this course?
        Can you add this course to my schedule?
        Can you remove this course from my schedule?
        Can you show me my schedule?
    '''

    def __init__(self):

        # Allows the model to use previous information.
        with open('tasks_and_prev_inputs.json') as file:
            tasks_and_prev_inputs = json.load(file)
        self.tasks_and_prev_inputs = tasks_and_prev_inputs

        tf_idf_matrix, idf_matrix = find_tf_idf(self.tasks_and_prev_inputs)

        # tf and idf information needed in the methods.
        self.tf_idf_matrix = tf_idf_matrix
        self.idf_matrix = idf_matrix

    def identify_task(self, input_string):
        '''
        Given an input, this method ranks all the tasks Phil knows how to do
        and returns a sorted list of the tasks most likely being requested.

        Input:
            input_string (str) - the user's input

        Output:
            ranked_tasks (lst) - a list with the most likely tasks at lower indexes
        '''

        input_string = clean_input(input_string)

        # Want to calculate the tf idf scores of the words in the input as if
        # they were part of tasks_and_prev_inputs already.
        ftapi = {"BLANK": input_string}

        task_freq_matrix = create_freq_matrix(ftapi)
        task_tf_matrix = create_tf_matrix(task_freq_matrix)

        # Using some formatting, we now have the tf idf scores of the words in the input
        task_tf_idf_matrix = create_tf_idf_matrix(task_tf_matrix, self.idf_matrix)["BLANK"]

        task_scores = []

        # Now we iterate through all tasks we have tf idf information for. We then look
        # at all the words in our input and generate a score for the task showing
        # how related the words in the request are to those already associated with the task.
        for task, tf_idf_table in self.tf_idf_matrix.items():

            score = 0

            for word, tf_idf_score in task_tf_idf_matrix.items():
                if word in tf_idf_table:

                    # Multiply the tf idf scores together to weight the effects of the more
                    # salient words in the input more. We then square this value to give a
                    # higher priority to more salient matches.
                    score += ((tf_idf_score * tf_idf_table[word]) ** 2)

            task_scores.append((score, task))

        ranked_tasks = [v[1] for v in sorted(task_scores, reverse=True)]

        return ranked_tasks

    def train_task(self, input_string, task_requested):
        '''
        Once a user selects which task they were actually requesting, we know that their
        input matches to that task. We can train the model on this to make it increasingly
        more accurate. This function recalculates tf_idf_matrix and idf_matrix with the new
        information.
        '''

        input_string = clean_input(input_string)

        # Future proofing so that it is easy to add new tasks that aren't currently
        # understood by Phil.
        if task_requested not in self.tasks_and_prev_inputs:
            self.tasks_and_prev_inputs[task_requested] = input_string

        elif self.tasks_and_prev_inputs[task_requested] == None:
            self.tasks_and_prev_inputs[task_requested] = input_string

        else:
            self.tasks_and_prev_inputs[task_requested] += (" " + input_string)

        self.tf_idf_matrix, self.idf_matrix = find_tf_idf(self.tasks_and_prev_inputs)

    def save_information(self):
        '''
        When a user ends their session we would like to store all the information we learned
        from them. This writes the updated tasks_and_prev_inputs to a json so that it can
        be used the next time we need it.
        '''

        with open('tasks_and_prev_inputs.json', 'w') as file:
            json.dump(self.tasks_and_prev_inputs, file)


def clean_input(input_string):
    '''
    Cleans an input_string. Normalizes for course_code by removing them and replacing them
    with COURSECODE. Thus a model trained on "What are prereqs for CMSC 12200?" still understands
    asking "What are the prereqs for MATH 18500?" is the same thing.
    Also makes use of nltk to reduce words to their basic stem. Means words like "prequisite" and
    "prerequisites" are understood to be the same thing.
    '''

    ps = PorterStemmer()

    clean_input = ""

    course_code = re.search("[A-Z]{4} [0-9]{5} *", input_string)
    if course_code:
        course_code = course_code.group()
        input_string = input_string.replace(course_code, " COURSECODE ")

    input_tokens = word_tokenize(input_string)
    for token in input_tokens:
        clean_input += (ps.stem(token) + " ")

    return clean_input

def find_tf_idf(tasks_and_prev_inputs):
    '''
    Master function to tie together all the helpers below it. Takes tasks_and_prev_inputs
    dictionary and calculates the tf_idf scores for all words in them.
    '''

    freq_matrix = create_freq_matrix(tasks_and_prev_inputs)

    tf_matrix = create_tf_matrix(freq_matrix)

    tasks_per_word_table = create_tasks_per_word(freq_matrix)

    idf_matrix = create_idf_matrix(tasks_and_prev_inputs, freq_matrix, tasks_per_word_table)

    tf_idf_matrix = create_tf_idf_matrix(tf_matrix, idf_matrix)

    return (tf_idf_matrix, idf_matrix)

def create_freq_matrix(tasks_and_prev_inputs):

    freq_matrix = {}
    ps = PorterStemmer()

    for task, prev_inputs in tasks_and_prev_inputs.items():

        freq_table = {}
        words = word_tokenize(prev_inputs)

        for word in words:
            if word in freq_table:
                freq_table[word] += 1
            else:
                freq_table[word] = 1

        freq_matrix[task] = freq_table

    return freq_matrix

def create_tf_matrix(freq_matrix):

    tf_matrix = {}

    for task, f_table in freq_matrix.items():

        tf_table = {}

        count_words = 0

        for word, count in f_table.items():
            count_words += count

        for word, count in f_table.items():
            tf_table[word] = count / count_words

        tf_matrix[task] = tf_table

    return tf_matrix

def create_tasks_per_word(freq_matrix):

    tasks_per_word_table = {}

    for task, f_table in freq_matrix.items():
        for word, _ in f_table.items():
            if word in tasks_per_word_table:
                tasks_per_word_table[word] += 1
            else:
                tasks_per_word_table[word] = 1

    return tasks_per_word_table

def create_idf_matrix(tasks_and_prev_inputs, freq_matrix, tasks_per_word_table):

    total_tasks = len(tasks_and_prev_inputs)

    idf_matrix = {}

    for task, f_table in freq_matrix.items():
        idf_table = {}

        for word in f_table.keys():
            idf_table[word] = math.log10(total_tasks / tasks_per_word_table[word])

        idf_matrix[task] = idf_table

    return idf_matrix

def create_tf_idf_matrix(tf_matrix, idf_matrix):

    tf_idf_matrix = {}

    for (task1, f_table1), (task2, f_table2) in zip(tf_matrix.items(), idf_matrix.items()):
        
        tf_idf_table = {}

        for (word1, value1), (word2, value2) in zip(f_table1.items(), f_table2.items()):

            tf_idf_table[word1] = float(value1 * value2)

        tf_idf_matrix[task1] = tf_idf_table

    return tf_idf_matrix


def build_tasks_and_prev_inputs():
    '''
    For developer use only. Allows someone to quickly train the model on a lot of new ways of
    requesting tasks.
    '''

    # tasks_to_build = ['What are the prerequisites for this course?',
    # 'Who are the instructors for this course?',
    # 'What are the equivalent courses for this course?',
    # 'Are these courses equivalent?',
    # 'What are the notes for this course?',
    # 'Which quarters is this course offered?',
    # 'What majors do you support?',
    # 'What requirements do I have left for my major?',
    # 'Do I meet the prerequisites for this course?',
    # 'Can you add this course to my schedule?',
    # 'Can you remove this course from my schedule?',
    # 'Can you show me my schedule?']

    with open('tasks_and_prev_inputs.json') as file:
        tasks_and_prev_inputs = json.load(file)

    ps = PorterStemmer()

    input_ = "XXX"

    for task in tasks_and_prev_inputs:

        while input_ != "STOP":
            input_ = input("\nAnother wording of " + task+ "\n\n>>>")

            if input_ != "STOP":

                course_code = re.search("[A-Z]{4} [0-9]{5} *", input_)
                if course_code:
                    course_code = course_code.group()
                    input_ = input_.replace(course_code, " COURSECODE ")

                input_tokens = word_tokenize(input_)
                for token in input_tokens:
                    tasks_and_prev_inputs[task] += (ps.stem(token) + " ")

        input_ = "XXX"

    with open('tasks_and_prev_inputs.json', 'w') as file:
        json.dump(tasks_and_prev_inputs, file)

    print(tasks_and_prev_inputs)