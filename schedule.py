# Winter '22 - CS122 Group Project - [insert group name here]

# Code for Schedule and Course Objects

# Omar Khan, Vidyut Baradwaj, Max Huisman

def class(schedule):
    
    def __init__(self):
        """
        Initializes a schedule object   
        Creates an empty list for each quarter of school for the student

        Inputs: 
            (self)

        Returns: Initialized schedule object
        """
        self.programs = ["CORE"] # Major(s) and/or minor(s) being pursued, always include "CORE" program
        self.fall1 = [] # One list per quarter where classes may be taken
        self.fall2 = []
        self.fall3 = []
        self.fall4 = []
        self.wint1 = []
        self.wint2 = []
        self.wint3 = []
        self.wint4 = []
        self.spr1 = []
        self.spr2 = []
        self.spr3 = []
        self.spr4 = []
        self.sum1 = []
        self.sum2 = []
        self.sum3 = []
        self.sum4 = []
        self.full_schedule = [] # make sure to add courses both to here and to specific quarter list

    def add_course(self, course):
        """
        Adds a course object to a list corresponding to the quarter it will
        be taken in

        Inputs: 
            (self)
            course : instance of a course object 

        Returns: nothing, edits object in place
        """

        #q = course.q
        self.q.append(course)

    def is_complete(self):
        """
        Checks the programs attribute of the schedule object to determine
        if the schedule meets all the core and program requirements for
        graduation.

        Inputs: 
            (self)

        Returns: (bool) True if schedule is complete, False if not
        """

        programs_list = { # to be filled in with scraper, then hand-edited
            "ECONBUS" : [],
            "ECONDS" : [],
            "ECONSTD" : [],
            "ECONMINOR" : [],
            "MATH" : [],
            "MATHMINOR" : [],
            "STAT" : [],
            "STATMINOR": [],
            "CORE": []
            # etc.
            }
        
        rv = True

        for program in self.programs:
            for course in progams_list[program]:
                if course not in self.full_schedule:
                    rv = False
        
        if len(self.full_schedule) < 42:
            rv = False
        
        
def class(course):

    def __init__(self, dept, course_num, title):
        """
        Initializes an instance of a course object.

        Inputs: 
            (self)
            dept (string): department code of the course eg. MATH
            course_num (int): course number code, eg. 15300
            title (string): title of the course eg. Calculus III
            
        Returns: course object
        """
        self.dept = dept
        self.course_num = course_num
        self.title = title
        

    def __repr__(self):
        """
        Returns a string representation of a course object

        Inputs:
            (self)

        Returns: (str) string representation eg.
                MATH 15300: Calculus III
        """
        self.full_string = dept + " " str(course_num) + ": " + title
        return self.full_string

    


