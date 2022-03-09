

import json
import tabulate
from tabulate import tabulate
import task_processing

file_ = open('scraped_data/prereqs2_data.json')

known_prereqs = json.load(file_)

# Schedule Class

class Schedule:

    def __init__(self, courses_taken, major=None):

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
            schedule[semester[0]][semester[1]].append(Course(course_code, semester))

        self.schedule = schedule

        self.major = major

        # Need to modify so this is called every time we add a course. Also make sure its never self.major=None
        _, reqs_unsatisfied, _ = task_processing.major_reqs_left_processing(self.courses_acc_for, self.major)

        if reqs_unsatisfied == []:
            major_complete = True
        else:
            major_complete = False

        self.major_complete = major_complete

    def add_course(self, course_code, semester, instructor="Not Specified"):

        _, unsatisfied_prereqs = task_processing.meet_course_prereqs_processing(self.courses_acc_for, course_code)

        if unsatisfied_prereqs == []:
            has_prereqs_warning = False
        else:
            has_prereqs_warning = True

        course_object = Course(course_code, semester, has_prereqs_warning, instructor)

        # Add to schedule
        self.schedule[semester[0]][semester[1]].append(course_object)

        # Update courses_acc_for
        self.courses_acc_for.add(course_code)

    def remove_course(self, rem_course_code):

        # Remove from schedule
        for year in self.schedule:
            for semester in year:
                for course_object in semester:
                    if course_object.course_code == rem_course_code:
                        semester.remove(course_object)
                        break
                break
            break

        # Update courses_acc_for
        self.courses_acc_for.remove(rem_course_code)

    def update_major(major):

        self.major = major
      

    # Make this into a nice repr
    def __repr__(self):

        num_to_semester = {0: "Autumn", 1: "Winter", 2: "Spring", 3: "Summer"}

        table = []

        max_courses = calc_max_courses(self.schedule)

        for i, year in enumerate(self.schedule):
            for j, semester in enumerate(year):

                if j == 0:
                    semester_row = ["Year " + str(i + 1)]
                else:
                    semester_row = [""]
                
                semester_row.append(num_to_semester[j])
                for course_object in semester:
                    semester_row.append(course_object)

                while len(semester_row) < max_courses:
                    semester_row.append("")

                table.append(semester_row)

        headers = ["", ""]
        for i in range(max_courses):
            headers.append("Course " + str(i + 1))

        return (tabulate(table, headers, tablefmt="grid"))

# Course Class

class Course:

    def __init__(self, course_code, semester_taking, has_prereqs_warning, instructor="Not specified"):

        self.course_code = course_code
        self.semester_taking = semester_taking
        self.instructor = instructor
        self.has_prereqs_warning = has_prereqs_warning

    def __repr__(self):

        str_repr = self.course_code + "\n"

        instructor_str = self.instructor
        if len(self.instructor) > 20:
            instructor_str = instructor_str[:17] + "..."
        str_repr += instructor_str + "\n"

        if self.has_prereqs_warning:
            str_repr += "(Prereqs!)\n"
        else:
            str_repr += "---\n"

        return str_repr


def calc_max_courses(schedule):

    max_courses = 0

    for year in schedule:
        for semester in year:
            if len(semester) > max_courses:
                max_courses = len(semester)

    return max_courses