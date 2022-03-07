
# Model that recognizes which task is being requested

import math
import re
import json

class Identifier:
    '''
    Class that helps identify which task the user is requesting and returns a ranked list of the most
    likely tasks. This class uses tf and idf scores.

    Tasks with existing code are:
        "Who teaches?", "When offered?", "What notes?", "What prereqs?", "What email?",
        "What equivalents?", "Give evaluations.", "Add course.", "Remove course.", "What major requirements?",
        "Check remaining major requirements."
    '''

    def __init__(self, max_queued_tasks, words_to_store):
        '''
        Constructor that initializes several important variables. Many are pulled from .json files because
        we want to leverage the requests of previous users to make more accurate rankings.
        '''

        self.max_queued_tasks = max_queued_tasks
        self.queued_tasks = 0
        self.words_to_store = words_to_store

        # A dictionary with tasks as keys and a single string concatenation of all ways this task has been
        # requested in the past as the value.
        with open('tasks_requested.json') as file:
            tasks_requested = json.load(file)
        self.tasks_requested = tasks_requested

        # A dictionary with tasks as keys and another dicionary as the value. This second dictionary contains
        # the top 20 tf/idf scoring words we have encountered before related to the task key and their scores.
        with open('tf_idf_map.json') as file:
            tf_idf_map = json.load(file)
        self.tf_idf_map = tf_idf_map
    
        # A dictionary with all words we have encountered before in any request and their idf.
        with open('word_idf_dict.json') as file:
            word_idf_dict = json.load(file)
        self.word_idf_dict = word_idf_dict

    def queue_task(self, input_string, task_requested):
        '''
        This method is closely related to train_task(). Ideally we would run train_task every time we get a
        new input/task pairing. However, this involves recalculating more and more things as we encounter more
        inputs, making the program take a while to respond. To ameliorate this wait time, every time we get a
        new pairing we only update its locations in tasks_requested and increment a counter.

        Once the counter reaches a specified maximum amount, it will trigger train_task().
        '''

        input_string, _ = Identifier.clean_input(self, input_string)

        if task_requested not in self.tasks_requested:
            self.tasks_requested[task_requested] = input_string
        elif self.tasks_requested[task_requested] == None:
            self.tasks_requested[task_requested] = input_string
        else:
            self.tasks_requested[task_requested] += (" " + input_string)

        self.queued_tasks += 1

        if self.queued_tasks > self.max_queued_tasks:
            Identifier.train_task(self)
            self.queued_tasks = 0

    def train_task(self):
        '''
        Once we have accumulated enough new pairings to warrant retraining our model, we recalculate idf and 
        tf scores and update their values in self.word_idf_dict and self.tf_idf_map
        '''

        self.word_idf_dict = calc_idf(self.tasks_requested)

        for task, prev_inputs in self.tasks_requested.items():
            if prev_inputs != None:

                top_words = Identifier.find_top_words(self, prev_inputs, self.words_to_store)

                top_dict = {}
                for score, word in top_words:
                    top_dict[word] = score

                self.tf_idf_map[task] = top_dict

        # Updates all our files with the newly calculated values.
        with open('tasks_requested.json', 'w') as file:
            json.dump(self.tasks_requested, file)

        with open('word_idf_dict.json', 'w') as file:
            json.dump(self.word_idf_dict, file)

        with open('tf_idf_map.json', 'w') as file:
            json.dump(self.tf_idf_map, file)

    def find_task(self, input_string):
        '''
        The main purpose of this class. Takes an input string and normalizes it using clean_input().
        Then it finds the 10 most imporant words in the input using tf_idf frequencies.

        It then goes through every task in self.tf_idf_map and sees whether one of these top 10 words
        is linked to the task. If so, it adds the square (to give greater weighting to matching more
        important words) of that word's tf/idf to the task's score.

        After having done this for all tasks, it has created a list of tuples of scores and tasks. It
        sorts these tuples and returns the ranked list of tasks with lower index tasks being more likely.
        '''

        input_string, course_code = Identifier.clean_input(self, input_string)

        top_words = Identifier.find_top_words(self, input_string, 10)

        task_scores = []

        # Loops through all tasks and calculates a score for them.
        for task, top_dict in self.tf_idf_map.items():
            if top_dict != None:

                score = 0

                for word in top_words:
                    if word[1] in top_dict:
                        score += (top_dict[word[1]] ** 2)

                score = score / 10

                task_scores.append((score, task))

        # Sorts tasks in decreasing order of score.
        task_scores = sorted(task_scores, reverse=True)

        ranked_tasks = [v[1] for v in task_scores]

        return (ranked_tasks, course_code)

    def find_top_words(self, string, max_amount):
        '''
        Helper function used in train_task() and find_task(). Takes a string and
        creates a sorted list of the most important words using tf/idf.

        Inputs:
            string (str) - the string to analyze
            max_amount (int) - the maximum number of words we care about

        Output:
            top_words (lst) - a sorted list of tuples of (tf/idf score, word)
        '''

        task_tf_dict = calc_tf(string)

        top_words = []

        for word, tf in task_tf_dict.items():
            if word in self.word_idf_dict:

                top_words.append((task_tf_dict[word] * self.word_idf_dict[word], word))

        top_words = sorted(top_words, reverse=True)
        if len(top_words) > max_amount:
            top_words = top_words[:max_amount]

        return top_words


    def clean_input(self, input_string):
        '''
        Cleans up input string for use in other methods.
        '''

        course_code = None

        course_code = re.search("[A-Z]{4} [0-9]{5} *", input_string)
        if course_code:
            course_code = course_code.group()
            input_string = input_string.replace(course_code, "!COURSECODE")

        input_string = input_string.lower()

        return (input_string, course_code)


def calc_tf(task_text):
    '''
    Takes a string and returns a dictionary with the tfs of every word in it
    '''

    task_tf_dict = {}

    task_text = task_text.split(" ")

    word_counts = {}
    for word in task_text:
        if word not in word_counts:
            word_counts[word] = 1
        else:
            word_counts[word] += 1

    max_count = 0
    for _, count in word_counts.items():
        if count > max_count:
            max_count = count
    
    for word, count in word_counts.items():
        word_tf = 0.5 + 0.5 * (count / max_count)
        task_tf_dict[word] = word_tf

    return task_tf_dict

def calc_idf(tasks_requested):
    '''
    Takes a dictionary of tasks and a string of all requests associated with the
    task and calculates the overall idf scores of all words that have ever appeared
    in a request.
    '''

    word_counts = {}

    word_idf_dict = {}

    for tasks in tasks_requested.values():
        if tasks != None:

            task_words = tasks.split(" ")

            for word in task_words:
                if word not in word_counts:
                    word_counts[word] = 1
                else:
                    word_counts[word] += 1

    for word in word_counts:

        word_idf = math.log(len(tasks_requested) / word_counts[word])

        word_idf_dict[word] = word_idf

    return word_idf_dict





        
