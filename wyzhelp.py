# file: wyzhelp.py
# useful routines for use with the main Wyz scripts
import re


def get_num_jobs(complete_file_path):
    '''Take a jobs html file and return an integer which
       is the total number of posted jobs (only 100 are in the file)'''
    fhand = open(complete_file_path,'r')
    for line in fhand:
        line = line.rstrip()
        if "<h2" in line:
            num_jobs = re.findall('<strong>(.+)</s', line)
            fhand.close()
            return int(num_jobs[0])
    fhand.close()
    # didn't find it?
    print("*** Didn't find number of jobs in: "+complete_file_path)
    return -1

def get_jobs_info(complete_file_path):
    '''Take a jobs html file and return a list consisting of
       a dictionary of information for each job.'''
    dictlist = []
    fhand = open(complete_file_path,'r')
    # Use a little state machine to go through the lines,
    # the immediate goal depends on the jstep value.
    jstep = 1
    for line in fhand:
        line = line.rstrip()

        if jstep == 1:
            # Each job starts with a <h4> ... </h4>, read until next one
            if not("</h4" in line): continue
            # got to the </h4> line, e.g. it looks like:
            # Physics Student in Evans, GA 30809                </h4>
            # Start the dictionary for this job
            this_dict={}
            #print(line)  # debug
            # extract various things from this line
            wyzsubj = re.findall('^(.+) Student in', line)
            city = re.findall('in (.+), \S\S [0-9]+', line)
            state = re.findall(', (\S\S) [0-9]+', line)
            zipstr = re.findall(', \S\S ([0-9]+)', line)
            this_dict['wyzsubj'] = wyzsubj[0]
            this_dict['city'] = city[0]
            this_dict['state'] = state[0]
            this_dict['zip'] = zipstr[0]
            # next step:
            jstep = 2
            continue

        if jstep == 2:
            # move on to find the student's request text,
            # between <p>  </p>OR</br>
            # might not be there: will hit <p class= in that case
            got_text = re.findall('<p>(.+)<', line)
            got_class = re.findall('<p class=', line)
            if ( len(got_text) == 0 and
                    len(got_class) == 0): continue
            # found one of them
            if len(got_class) != 0:
                this_dict['jobtext'] = '(No Job Text)'
            else:
                this_dict['jobtext'] = got_text[0]
            jstep = 3
            continue

        if jstep == 3:
            # move on to find the WyzAnt ID number, e.g:
            #     <a class="hide-4173179 hide
            #    OR
            # might hit the Posted line - no WyzAnt ID number?!?!
            # in this case mention it, skip it and go back to step 1
            got_posted = re.findall('- Posted by (.+), <', line)
            if len(got_posted) != 0:
                # really messed up format - no wyzant id etc
                print(" * * * No WyzAnt ID * * * Posted by "+
                        got_posted[0]+" in "+this_dict['zip'])
                jstep = 1
                continue
            got_wid = re.findall('class="hide-([0-9]+) hide', line)
            if len(got_wid) == 0: continue
            # found it
            this_dict['wyzid'] = int(got_wid[0])
            jstep = 4
            continue

        if jstep == 4:
            # move on to find the Student grade level:
            # which is then on the next line.
            # Might not be there: will hit "- Posted by " in that case
            #  - don't continue just let it go to step 8, which wants Posted
            got_grade = re.findall('Student grade level:', line)
            if len(got_grade) != 0:
                # OK, found it.  Now go to step 5 and next line.
                jstep = 5
                continue
            # Check if we've passed it (not there)
            got_posted = re.findall('- Posted by (.+), <', line)
            if len(got_posted) != 0:
                # it's not there
                this_dict['grade'] = '(Not Given)'
                jstep = 8
            # no continue: want the current line to go to step 8

        if jstep == 5:
            # This line should have <span> with grade level:
            got_grade = re.findall('<span>(.+)<', line)
            if len(got_grade) == 0:
                print(" *** Ooops! *** Didn't find grade level")
                jstep = 8
            else:
                this_dict['grade'] = got_grade[0]
                jstep = 8
            continue

        if jstep == 8:
            # move to the Posted line, looks like:
            # >- Posted by Ashaki, <time datetime="2017-12-04">11 hours ago</time>
            got_posted = re.findall('- Posted by (.+), <', line)
            if len(got_posted) == 0: continue
            # found it
            this_dict['name'] = got_posted[0]
            # get the posted date too
            postdate = re.findall('datetime="(.+)">', line)
            this_dict['postdate'] = postdate[0]
            jstep = 9 # all done
            continue

        if jstep == 9:
            # this job's dictionary is all assembled, add it to the list
            dictlist.append(this_dict)
            # and look for another job
            jstep = 1

    # all finished with the file
    return dictlist
