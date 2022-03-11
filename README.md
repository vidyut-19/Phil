Phil the ChatBot - CS 122 Group Project by Max Huisman, Vidyut Baradwaj, and Omar Khan

Motivation:
As UChicago students, we are already stressed by the time pre-registration comes around during Week 7. 
While Academic advisors exist, they're not the most accessible during times of need. So, we felt
there was a need for an interactive program that answers questions students may have when picking courses,
such as what prerequisites a class has, who teaches it, when is it offered, and whether the student fulfills    
the requirement to complete a given course and what students thought about a particular course among others. 
It's easier to use than Stellic, easier to reach than your academic advisor, and wittier than anyone you know!

Hope you enjoy talking to Phil, just as much as he will talking to you :)

Phil's Capabilities:

    1. Who are the instructors for this course?
    2. Which quarters is this course offered?
    3. What requirements do I have left for my major?
    4. What majors do you support?
    5. What do people think about a certain aspect of this course?
    6. What did people think about this course?
    7. What are the prerequisites for this course?
    8. What are the notes for this course?
    9. What are the equivalent courses for this course?
    10. Submit a comment to my developers.
    11. Do I meet the prerequisites for this course?
    12. Can you show me my schedule?
    13. Can you remove this course from my schedule?
    14. Can you change my major?
    15. Can you add this course to my schedule?
    16. Are these courses equivalent?



Instructions:
We have implemented two UIs:
1. An interactive text-based interface that includes all of Phil's functionalites
Instructions to run:
- in this directory, type "python3 running_code"

2. A Flask-powered web-application that only answers questions relating to course evaluations
Instructions to run:
- enter the chatbot_deployment directory
- type "python3 app.py" in the terminal to activate the web app 
- ctrl + click on the local link that appears in the terminal, opening up a python window

(Warning: you must have Flask version 2 or above installed in python3 for the app to run)

This is an overview of all the files and directories in CS122-Group-Project

Modules and packages you will need: 
Selenium
Flask (2 or above)
Tabulate
vaderSentiment
sqlite3

Please ensure you're running Phil with Mozilla Firefox installed in a Linux environment

>>> Files - starred (***) items are important to the project:

    Crucial to project
    --------------------------------------------

    *** running_code.py - the most important file here. Connects together everything and runs the
    terminal based user interface. [commented] - Max

    *** task_processing.py - contains the functions that carry out the various tasks the bot can do.
    Called in running_code.py to answer many tasks. [commented] - Omar, Max, Vidyut

    *** classes.py - the schedule and course objects that are used to keep track of the user's schedule [commented] - Max, Omar

    *** identify_tasks.py - a class that is used to understand what a user is trying to ask. Uses tf-idf
    scores to identify the most likely request and trains itself as the program is used. [commented] - Max

    *** tasks_and_prev_inputs.json - a json document that stores the tasks_and_prev_inputs dictionary
    used by identify_tasks.py. - Max

    *** suggested_questions.csv - a csv containing the outputs of "Submit a comment to my developers."
    in running_code.py. Devs can look at this and see what users want them to implement. - Max, Omar


    Disregard
    --------------------------------------------

    'Project Brainstorming.pdf' - original brainstorming document

    schedule.py - test version of schedule class

    testui.py - experiments in GUI - Max

    'course eval search' - no idea

    suggestions.py - rough draft of task_processing

    check_prereqs.py - discarded rough draft of old task - Max

    salients.py

    geckodriver.log - autogenerated log for the Selenium Firefox log
 


>>> Directories - starred (***) items are important to the project.
    Scroll down to see more in-depth info on *** directories.

    Crucial to Project
    --------------------------------------------

    *** scraping - directory that contains all the code used for scraping course catalog - Max

    *** scraped_data - directory containing all the scraped data used by the project - Max

    *** chatbot-deployment - directory containing fron-end elements for web-app implementation using Flask - Vidyut

    Disregard
    --------------------------------------------

    identify_ques - old directory initially used to develop identify_tasks.py


>>> More information on - scraping

    Crucial to Project
    --------------------------------------------

    *** course_scraping.py - bodged code to scrape information about courses from the course
    catalog and write them to various csv files. - Max

    *** process.py - helper functions for making sense of scraped information in course_scraping.py - Max

    *** major_scraping.py - code to scrape major information from course catalog. Not perfect
    and requires a human to check over the json file it produces but this is not intensive. - Max

    *** instructor_extra.py - uses the UChicago directory to find the full name of an instructor
    and their email if possible. - Max

    *** pa2util.py - code taken from PA 2 to help with the automatic link traversal used in
    course_scraping.py.


    Disregard
    --------------------------------------------

    major_reqs_data.json - old info

    major_reqs_data_BACKUP.json - backup

    prereqs1_text.csv - old info

    check_prereqs.py - obsolete code


>>> More information on - scraped_data

    Crucial to Project
    --------------------------------------------

    data.db - database that stores all information in these csv files - Omar

    major_reqs_data.json - json file storing major requirement information - Max

    prereqs2_data.json - json file of courses and semi-accurate digitalized version of their prereqs1_text - Max

    For information on any of the .csv files, look at README.txt in this directory - Max

>>> More information on - chatbot_deployment

    

    Disregard
    --------------------------------------------
    chat.py

    intents.json

    nltk_utils.py

    train.py


    