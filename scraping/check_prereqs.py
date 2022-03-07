
# Given a list of courses a student has taken and a course's prereqs, this program determines whether the
# student meets all the prerequirements to enroll.

def meet_requirements(courses_taken, requirements):
    '''
    Determines whether a student has satisfied all the requirements to be able
    to enroll in a course.

    Inputs:
        courses_taken (list): a list of all the courses a student has taken
        course_prereqs (list): a structure of nested lists representing prereqs for a course

    Outputs:
        rv (bool): a boolean that is True if requirements are met and False if not
    '''

    reqs_met = recursive_helper(courses_taken, requirements)

    if reqs_met == 1:
        return True

    elif reqs_met == 0:
        return False

    return reqs_met


def recursive_helper(courses_taken, options_poss):

    bool_output = True

    for track in options_poss:
        
        if isinstance(track[0], list):
            bool_output = bool_output * recursive_helper(courses_taken, track)

        else:

            track_score = 0

            for course in track:
                
                if isinstance(course, set):
                    for sub_course in course:
                        if sub_course not in courses_taken:
                            bool_output *= 0

                elif course in courses_taken:
                    track_score += 1

            if track_score == 0:
                bool_output *= 0

    return bool_output


            

            
