

import json

file_ = open('scraped_data/prereqs2_data.json')

known_prereqs = json.load(file_)

# Schedule Class

class Schedule:

    def __init__(self, major, courses_taken, current_semester):

        # Basic info
        self.majors = majors
        self.current_semester = current_semester

        # A list of tuples (course code, (Y, S))
        self.courses_taken = courses_taken

        courses_acc_for = set()
        for course_code, _ in self.courses_taken:
            courses_acc_for.add(course_code)
        self.courses_acc_for = courses_acc_for

        # Building schedule
        schedule = []

        for i in range(4):
            schedule.append([])
            for j in range(4):
                schedule[i].append([])

        for course_code, semester in courses_taken:
            schedule[semester[0]][semester[1]].append(course_code)

        self.schedule = schedule

    def add_course(self, course_code, semester):

        if course_code in courses_acc_for:
            pass

        else:
        self.schedule[semester[0]][semester[1]].append(course_code)
        self.courses_taken.append((course_code, semester))

    # remove course



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
        
