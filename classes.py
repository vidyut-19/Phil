

import json

file_ = open('scraped_data/prereqs2_data.json')

known_prereqs = json.load(file_)

# Schedule Class

class Schedule:

    def __init__(self, majors, courses_taken, current_semester):

        self.majors = majors

        #self.major_requirements = ...

        # A list of tuples (course code, (Y, S))
        self.courses_taken = courses_taken
        self.current_semester = current_semester

        schedule = []

        for i in range(4):
            schedule.append([])
            for j in range(4):
                schedule[i].append([])

        for course_code, semester in courses_taken:
            schedule[semester[0]][semester[1]].append(course_code)

        self.schedule = schedule

    def add_course(self, course_code, semester):

        # check if course is already in schedule
        # 

        self.schedule[semester[0]][semester[1]].append(course_code)
        self.courses_taken.append((course_code, semester))

    def remove_course(self, course_code):
        """
        """
        is_course = False
        for semester in schedule:
            replacement_lst = []
            for course in semester:
                if course != course_code:
                    replacement_lst.append(course)
                else:
                    is_course = True
            if is_course:
                semester = replacement_lst
        
        



    def draw_schedule(self):

        print("--------------------------------------------------")
        for i in range(4):
            print("YEAR: ", i+1)
            for j in range(4):
                print("--------------------------------------------------")
                print("SEMESTER: ", j+1)
                print(self.schedule[i][j])
        print("--------------------------------------------------")

# Course Class

class Course:

    def __init__(self, course_code, semester_taking, instructor):

        self.course_code = course_code
        self.semester_taking = semester_taking
        self.instructor = instructor

        if course_code in known_prereqs.keys():
            prereqs = known_prereqs[course_code]
        else:
            prereqs = []

        self.prereqs = prereqs
        
