from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import random
import json
#import os
#import sys
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
#current = os.path.dirname(os.path.realpath(__file__))
#parent = os.path.dirname(current)
#sys.path.append(parent)
#from task_processing import prerequisites, terms, notes, professors
options = webdriver.FirefoxOptions()
options.headless = True


def get_response(string_input):
    '''
    assigns processing function based on given string input
    '''
    if len(string_input) > 10:
        course_code, aspect = tuple(string_input.split(', ')) 
        #if 'prereq' in aspect:
        #    return str(prerequisites(course))
        #elif 'terms' in aspect:
        #    return str(terms(course))
        #elif 'notes' in aspect:
        #   return str(notes(course))
        #elif 'professors' in aspect:
            #return str(professors(course))
        return get_course_eval(course_code, aspect)
    else:
        return analyzer(string_input)
    
# time permitting, would have rather implemented a JSON that maps questions to respective functions in task_processing instead of multiple if statements

def get_course_eval(course_code, aspect=None):
    '''
    Scrapes course evals and outputs a dictionary containing comments for select common questions
    Inputs - (str) dept name (XXXX) and course_code (12345)
    Output - comments (dict) mapping attribute of course eval to set of comments (str)
    '''

    dept_name, course_code = tuple(course_code.split())

    driver = webdriver.Firefox(executable_path = './geckodriver')
    driver.get(f'https://coursefeedback.uchicago.edu/?CourseDepartment={dept_name}&CourseNumber={course_code}')
    element0 = WebDriverWait(driver, 50).until(EC.title_is(("Log in to Your UChicago Account")))
    if driver.current_url == "https://shibboleth2.uchicago.edu/idp/profile/SAML2/Redirect/SSO?execution=e1s2":
        element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "username")))
    element2 =  WebDriverWait(driver, 30).until(EC.title_is(("Duo Login")))
    element3 =  WebDriverWait(driver, 30).until(EC.title_is(("Course Feedback | The University of Chicago")))
    comments = {'gains' : set(), 'aspects' : set(), 'additional comments' : set(),  'difficulty' : set(), 'instructor features' : set(), 'sources for improvement' : set()}
    element4 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="evalSearchResults"]/thead/tr/th[2]')))
    driver.find_element_by_xpath('//*[@id="evalSearchResults"]/thead/tr/th[4]').click()
    element5 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="evalSearchResults"]/thead/tr/th[2]')))
    driver.find_element_by_xpath('//*[@id="evalSearchResults"]/thead/tr/th[4]').click()
    
    for i in range(3):
        element6 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="evalSearchResults"]/tbody/tr[{i + 1}]/td[1]/a')))
        driver.find_element_by_xpath(f'//*[@id="evalSearchResults"]/tbody/tr[{i + 1}]/td[1]/a').click()
        driver.switch_to.window(driver.window_handles[i + 1])
        element7 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'report-block')))
        q_lst = driver.find_elements_by_class_name('report-block')

        for q in q_lst:
            if "What are the most important things that you learned in this course? Please reflect on the knowledge and skills you gained." in q.text:
                comments['gains'].update(q.text.split('\n')[3:])                
            elif "What could she/he modify to help you learn more?" in q.text or "What could the instructor modify to help you learn more?" in q.text:
                comments['sources for improvement'].update(q.text.split('\n')[3:])               
            elif "What aspect of the instructor's teaching contributed most to your learning?" in q.text or "Thinking about your time in class, what aspect of the instructor's teaching contributed most to your learning?" in q.text:
                comments['instructor features'].update(q.text.split('\n')[3:])
            elif "Please comment on the level of difficulty of the course relative to your background and experience." in q.text:
                print(q.text.split('\n')[3:])
                comments['difficulty'].update(q.text.split('\n')[3:])
            elif "Describe how aspects of this course (lectures, discussions, labs, assignments, etc.) contributed to your learning." in q.text:
                comments['aspects'].update(q.text.split('\n')[3:])
            elif "Additional Comments about this course" in q.text:
                comments['additional comments'].update(q.text.split('\n')[3:])
        driver.switch_to.window(driver.window_handles[0])

    driver.close()
    driver.quit()
    if aspect != None:
        rv = "Comments: \n"
        str_output = ("\nHere are %d comments I found about %s's \"%s\" aspect:") % (min(len(comments[aspect]), 5), course_code, aspect)

        for i, comment in enumerate(list(comments[aspect])):
            if i < 4:
                str_output += ("    " + str(i + 1) + ". " + comment + "\n")
            else:
                break
        return str_output
    else:
        return comments

    
def analyzer(course_code):
    '''
    Conducts sentiment analysis on comments scraped from course evaluations using
    VADER sentiment
    Inputs: 
        course_code (str)
    Returns:
        verdict (str)
    '''
    comments = get_course_eval(course_code)
    if len(comments) == 0:
        return "Sorry, you seem to have entered a course that either doesn't have evaluations or doesn't exist."
    analyzer_ = SentimentIntensityAnalyzer()
    neg, pos, neu = 0, 0, 0
    n = 0
    for c_set in comments.values():
        for c in c_set:
            senti_dict = analyzer_.polarity_scores(c)
            neg += senti_dict['neg']
            pos += senti_dict['pos']
            neu += senti_dict['neu']
            n += 1

    neg = round((neg / n) * 100, 1)
    pos = round((pos / n) * 100, 1)
    neu = round((neu / n) * 100, 1)

    return f"Overall, evals for this course were {pos}% positive, {neg}% negative" + f" and {neu}% neutral"


