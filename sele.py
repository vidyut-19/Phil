from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import random
import salients
import json
import nltk
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
nltk.download('stopwords')
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
analyzer = SentimentIntensityAnalyzer()



options = webdriver.FirefoxOptions()
options.headless = True

def get_course_eval(dept_name, course_code):
    '''

    '''
    driver = webdriver.Firefox(executable_path = '/home/vidyut/CS122-Group-Project/geckodriver')
    driver.get(f'https://coursefeedback.uchicago.edu/?CourseDepartment={dept_name}&CourseNumber={course_code}')
    element0 = WebDriverWait(driver, 5).until(EC.title_is(("Log in to Your UChicago Account")))
    if driver.current_url == "https://shibboleth2.uchicago.edu/idp/profile/SAML2/Redirect/SSO?execution=e1s2":
        element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "username")))
    element2 =  WebDriverWait(driver, 30).until(EC.title_is(("Duo Login")))
    element3 =  WebDriverWait(driver, 60).until(EC.title_is(("Course Feedback | The University of Chicago")))
    comments = {'gains' : set(), 'aspects' : set(), 'add_comments' : set(),  'difficulty' : set(), 'inst_features' : set(), 'inst_impr' : set()}
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
                comments['inst_impr'].update(q.text.split('\n')[3:])               
            elif "What aspect of the instructor's teaching contributed most to your learning?" in q.text or "Thinking about your time in class, what aspect of the instructor's teaching contributed most to your learning?" in q.text:
                comments['inst_features'].update(q.text.split('\n')[3:])
            elif "Please comment on the level of difficulty of the course relative to your background and experience." in q.text:
                comments['difficulty'].update(q.text.split('\n')[3:])
            elif "Describe how aspects of this course (lectures, discussions, labs, assignments, etc.) contributed to your learning." in q.text:
                comments['aspects'].update(q.text.split('\n')[3:])
            elif "Additional Comments about this course" in q.text:
                comments['add_comments'].update(q.text.split('\n')[3:])
        driver.switch_to.window(driver.window_handles[0])

    return comments
    #top_k = salients.find_top_k_ngrams(comments[aspect], n, False, k)
    
def analyzer(comments):
    for c in comments.values(): 
        tokenized_words = word_tokenize(c)
        for w in tokenized_words:
            if w not in set(stopwords.words("english")):
