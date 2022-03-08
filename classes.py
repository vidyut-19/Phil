

import json
import tabulate
from tabulate import tabulate

file_ = open('scraped_data/prereqs2_data.json')

known_prereqs = json.load(file_)

# Schedule Class

class Schedule:

    def __init__(self, courses_taken, current_semester, major=None):

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

        # Break out code in task processing to be able to give me a true false boolean
        #self.major_complete = False
        self.current_semester = current_semester

    def add_course(self, course_code, semester, instructor="Not Specified"):

        course_object = Course(course_code, semester, instructor)

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

            # year_row = ["Year: " + str(i)]
            # for k in range(max_courses):
            #     year_row.append("")

            # table.append(year_row)

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

    def __init__(self, course_code, semester_taking, instructor="Not specified"):

        self.course_code = course_code
        self.semester_taking = semester_taking
        self.instructor = instructor

        # need to break up code in task processing to be able to give
        # me a true false value
        self.has_prereqs_warning = False

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