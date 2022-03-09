import unicodedata
import sys
import json
import math

def keep_chr(ch):
    '''
    Find all characters that are classifed as punctuation in Unicode
    (except #, @, &) and combine them into a single string.
    '''
    return unicodedata.category(ch).startswith('P') and \
        (ch not in ("#", "@", "&"))

PUNCTUATION = " ".join([chr(i) for i in range(sys.maxunicode)
                        if keep_chr(chr(i))])

# When processing tweets, ignore these words
STOP_WORDS = ["a", "an", "the", "this", "that", "of", "for", "or",
              "and", "on", "to", "be", "if", "we", "you", "in", "is",
              "at", "it", "rt", "mt", "with", "i", "had", "was", "as", "were"]

# When processing tweets, words w/ a prefix that appears in this list
# should be ignored.
STOP_PREFIXES = ("@", "#", "http", "&amp")


def sort_count_pairs(l):
    '''
    Sort pairs using the second value as the primary sort key and the
    first value as the seconary sort key.

    Inputs:
       l: list of pairs.

    Returns: list of key/value pairs

    Example use:
    In [1]: import util

    In [2]: util.sort_count_pairs([('D', 5), ('C', 2), ('A', 3), ('B', 2)])
    Out[2]: [('D', 5), ('A', 3), ('B', 2), ('C', 2)]

    In [3]: util.sort_count_pairs([('C', 2), ('A', 3), ('B', 7), ('D', 5)])
    Out[3]: [('B', 7), ('D', 5), ('A', 3), ('C', 2)]
    '''
    return list(sorted(l, key=cmp_to_key(cmp_count_tuples)))

#Make lint be quiet.
#pylint: disable-msg=unused-argument, too-few-public-methods

def cmp_to_key(mycmp):
    '''
    Convert a cmp= function into a key= function
    From: https://docs.python.org/3/howto/sorting.html
    '''

    class CmpFn:
        '''
        Compare function class.
        '''
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return CmpFn


def cmp_count_tuples(t0, t1):
    '''
    Compare pairs using the second value as the primary key and the
    first value as the secondary key.  Order the primary key in
    non-increasing order and the secondary key in non-decreasing
    order.

    Inputs:
        t0: pair
        t1: pair

    Returns: -1, 0, 1

    Sample uses:
        cmp(("A", 3), ("B", 2)) => -1

        cmp(("A", 2), ("B", 3)) => 1

        cmp(("A", 3), ("B", 3)) => -1

        cmp(("A", 3), ("A", 3))
    '''
    (key0, val0) = t0
    (key1, val1) = t1
    if val0 > val1:
        return -1

    if val0 < val1:
        return 1

    if key0 < key1:
        return -1

    if key0 > key1:
        return 1

    return 0

def count_tokens(tokens):
    '''
    Counts each distinct token (entity) in a list of tokens.

    Inputs:
        tokens: list of tokens (must be immutable)

    Returns: dictionary that maps tokens to counts
    '''
    token_dict = {}

    for token in tokens:
        if token not in token_dict: 
            token_dict[token] = 1
        else:
            token_dict[token] += 1
    return token_dict


# Task 1.2
def find_top_k(tokens, k):
    '''
    Find the k most frequently occuring tokens.

    Inputs:
        tokens: list of tokens (must be immutable)
        k: a non-negative integer

    Returns: list of the top k tokens ordered by count.
    '''

    #Error checking (DO NOT MODIFY)
    if k < 0:
        raise ValueError("In find_top_k, k must be a non-negative integer")

    token_dict = count_tokens(tokens)
    token_list = []

    for token, count in token_dict.items():
        token_list.append((token, count))
    sorted_list = sort_count_pairs(token_list) 

    lst2 = []
    for tuple in sorted_list:
        lst2.append(tuple[0])

    return lst2[:k]


def find_min_count(tokens, min_count):
    '''
    Find the tokens that occur *at least* min_count times.

    Inputs:
        tokens: a list of tokens  (must be immutable)
        min_count: a non-negative integer

    Returns: set of tokens
    '''

    #Error checking (DO NOT MODIFY)
    if min_count < 0:
        raise ValueError("min_count must be a non-negative integer")
    
    token_set = set()
    token_dict = count_tokens(tokens)

    for token, count in token_dict.items():
        if count >= min_count:
            token_set.add(token)

    return token_set


def count_dicts_maker(docs):
    """
    Takes a list of lists and returns a dictionary mapping each word to its count

    Input:
        docs: a list of lists

    Returns: list of dictionaries mapping word to count within each doc
    """
    rv = []

    for doc in docs:
        count_dict = count_tokens(doc)
        rv.append(count_dict)

    return rv


def compute_idf(docs):
    """
    Takes a list of lists and calculates the idf value for each word occuring in the list
    Input:
        docs: a list of lists
    
    Returns: a dictionary mapping each word to its idf values
    """
    count_dicts = count_dicts_maker(docs)
    doc_count = len(docs)

    appears_in_docs = {} 
    for count_dict in count_dicts:
        for word in count_dict:
            counter = 0
            for count_dict in count_dicts:
                if word in count_dict:
                    counter += 1
            appears_in_docs[word] = counter
                
    idfs = {}
    for word in appears_in_docs:
        idfs[word] = math.log(doc_count / appears_in_docs[word])

    return idfs 

   
def find_salient(docs, threshold):
    '''
    Compute the salient words for each document.  A word is salient if
    its tf-idf score is strictly above a given threshold.

    Inputs:
      docs: list of list of tokens
      threshold: float

    Returns: list of sets of salient words
    '''

    count_dicts = count_dicts_maker(docs)
    idfs = compute_idf(docs)
    rv = []
    for i, doc in enumerate(docs):
        salients = set()
        if doc == []:
            rv.append(set())
            continue
        count_dict = count_dicts[i]
        all_counts = count_dict.values()
        max_word = max(all_counts)
        for word in doc:
            tf_idf = idfs[word] * (0.5 + 0.5*(count_dict[word] / max_word))
            if tf_idf > threshold:
                salients.add(word)
        rv.append(salients)
   
    return rv

def sentence_splitter(tweet):
    """
    For given text, returns a list of each word in the text
    Input:
        tweet: string
    Returns:
        list of strings
    """
    rv = tweet.split()
    return rv


def word_cleaner(word_list, case_sensitive, omit_stop_words):
    """
    Pre-processing step that filters and cleans the list of strings"
    Inputs:
        word_list = list of words
        case_sensitve = boolean
        omit_stop_words = boolean
    Returns:
        a list of words 
    """
    cleaned_word_list = []
    for word in word_list:
        word = word.strip(PUNCTUATION)
        if word == "":
            continue
        if not case_sensitive:
            word = word.lower()
        if omit_stop_words:
            if word in STOP_WORDS:
                continue
        for prefix in STOP_PREFIXES:
            if word.startswith(prefix):
                word = ""
        if word == "":
            continue
        cleaned_word_list.append(word)

    return cleaned_word_list


def rep_n_grams(word_list, n):
    """
    Pre-processing step that represents the list of words as n-grams
    Input:
        word_list: cleaned list of words
        n: integer
    Returns:    
        list of n-grams
    """
    rv = []
    for i, _ in enumerate(word_list):
        if i == len(word_list) - (n-1):
            break
        n_gram = tuple(word_list[i:i + n])  
        rv.append(n_gram)
    return rv


def n_gram_collector(tweets, n, case_sensitive, omit_stop_words):
    """
    Does all of the pre-processing for all tweets
    Inputs:
        tweets: list of lists
        n : integer for n-grams
        case_sensitive: boolean
        omit_stop_words: boolean
    Returns:
        list of all n_grams
    """
    rv = []
    for tweet in tweets:
        word_list = sentence_splitter(tweet)
        word_list = word_cleaner(word_list, case_sensitive, omit_stop_words)
        n_grams= rep_n_grams(word_list, n)
        rv.extend(n_grams)

    return rv

def find_top_k_ngrams(tweets, n, case_sensitive, k):
    '''
    Find k most frequently occurring n-grams.

    Inputs:
        tweets: a list of tweets
        n: integer
        case_sensitive: boolean
        k: integer

    Returns: list of n-grams
    '''
    omit_stop_words = True
    rv = []
    n_grams = n_gram_collector(tweets, n, case_sensitive, omit_stop_words)
    
    rv = find_top_k(n_grams, k)
    
    return rv


# Task 3.2
def find_min_count_ngrams(tweets, n, case_sensitive, min_count):
    '''
    Find n-grams that occur at least min_count times.

    Inputs:
        tweets: a list of tweets
        n: integer
        case_sensitive: boolean
        min_count: integer

    Returns: set of n-grams
    '''

    omit_stop_words = True
    rv = set()
    n_grams = n_gram_collector(tweets, n, case_sensitive, omit_stop_words)
    rv  = find_min_count(n_grams, min_count)

    return rv


# Task 3.3
def find_salient_ngrams(tweets, n, case_sensitive, threshold):
    '''
    Find the salient n-grams for each tweet.

    Inputs:
        tweets: a list of tweets
        n: integer
        case_sensitive: boolean
        threshold: float

    Returns: list of sets of strings
    '''

    omit_stop_words = False
    rv = []
    all_n_grams = []
    for tweet in tweets:
        word_list = sentence_splitter(tweet)
        word_list = word_cleaner(word_list, case_sensitive, omit_stop_words)
        n_grams= rep_n_grams(word_list, n)
        all_n_grams.append(n_grams)
    
    rv = find_salient(all_n_grams, threshold)
   
    return rv