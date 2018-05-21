# file: WyzIngest.py
#
# Ingest (any new) daily data files into database tables.
#
# update 2018-02-07:
#  - include wyzadded field in database: the change in wyzidhi values.
#  - if there are no new jobs in a file (unlikely but it happened),
#    then its wyzidhi is taken from the previous file's wyzidhi.
# update 2018-01-11:
#  - account for more than one-day-apart files
#    (e.g., no valid 2017-11-24 or 2017-12-26)

import os
import sqlite3
#import time
#import string
#import re
from datetime import datetime, timedelta
#import dateutil.parser as parser

# Put various subroutines used by this file:
import wyzhelp

# - - - Get the files - - -
# Daily files directory
dailydir = ("WyzAntDaily_Data")
# Get all appropriate files
try:
    files = os.listdir(dailydir)
except:
    print("*** Error looking in dir: "+dailydir)
    files =[]
if len(files) == 0:
    print("No files found in dir: "+dailydir)
    quit()
print("Found "+str(len(files))+" files in the Daily dir...")

# - - - Open and setup the database - - -
dbconn = sqlite3.connect('wyzjobs.sqlite')
dbcur = dbconn.cursor()

# ... Table of ZIP codes ...
# This table, Zips, is loaded before the ongoing WyzAnt jobs data,
# it is defined and filled-in by the routine:
#     ZIPload.py
# Zips contains fields: izip, popul, lowinc
# Although not relational-database-ly proper to duplicate data,
# the Job's zip is used below to copy/fill lowinc into the Jobs table.

# Setup the db tables as needed

# ... Table of files ...
# Information about the (usually) daily monitoring files of job listings
# Can start from scratch while testing or reprocessing
##dbcur.execute('DROP TABLE IF EXISTS Files')
dbcur.execute('''CREATE TABLE IF NOT EXISTS Files
                (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                name VARCHAR(128),
                dtstr VARCHAR(32),
                njobs INTEGER,
                nadded INTEGER,
                wyzidlo INTEGER,
                wyzidhi INTEGER,
                wyzadded INTEGER )''')

# ... Table of Jobs ...
# Information about the jobs is some integers:
#   id, file_id, lastfile_id, verified, dayson, wyzid
# and then a bunch of strings:
#   wyzsubj, [city, state,] zip, jobtext, grade, [name,]
# Can start from scratch while testing or reprocessing
##dbcur.execute('DROP TABLE IF EXISTS Jobs')
dbcur.execute('''CREATE TABLE IF NOT EXISTS Jobs
                (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                file_id INTEGER, lastfile_id INTEGER, verified INTEGER,
                dayson INTEGER, zip VARCHAR(8), lowinc REAL,
                wyzid INTEGER, wyzsubj VARCHAR(16), grade VARCHAR(16),
                name VARCHAR(32), jobtext VARCHAR )''')

# - - - Add any new files - - -
# Sort files (by name ~ date code)
files.sort()
# Check them and get the (creation) times for the good files
# * One kuldge: file 2017-11-06_A.html is a catted together of A and B
#   in order to pre-load some older jobs too.
#   Because of this its datetime has to be adjusted in the code.
#   It should be: 2017-11-16T08:27:44.158575
#
fsadded=0
print("Valid files in the dir are:")
for filename in files:
    if "_A.html" not in filename:
        continue  # nope, next file
    # Fix any file date/times...
    if filename == '2017-11-16_A.html':
        fdtime = '2017-11-16T08:27:44.158575'
    # Initially saved these two with 2011 year(?) -
    # did 'mv' to change file names to 2017;
    # this preserved the original date/times (put them here just in case):
    # 2011[7]-12-13_A.html 349 2017-12-13T07:51:18.458400
    # 2011[7]-12-15_A.html 352 2017-12-15T08:38:02.406782
    else:
        # use the st_mtime value
        ftime = os.stat(dailydir+"/"+filename).st_mtime
        # put it in datetime ISO format (a string)
        fdtime = datetime.fromtimestamp(ftime).isoformat()
    # Get the total number of jobs posted
    fnumjobs = wyzhelp.get_num_jobs(dailydir+"/"+filename)
    print("   ",filename, fnumjobs, fdtime)

    # Has this file already been ingested?
    dbcur.execute('SELECT name FROM Files WHERE name=?', ( filename, ) )
    row = dbcur.fetchone()
    if row == None:
        fsadded += 1
        dbcur.execute('''INSERT INTO Files
                        (name, dtstr, njobs, nadded)
                        VALUES ( ? , ? , ? , -1)''',
                        (filename, fdtime, fnumjobs) )
dbconn.commit()
print("Added "+str(fsadded)+" files to the Files table.\n")

# - - - Ingest the first un-ingested (nadded=-1) file into Jobs table
#       Using the date/time string here for file order
dbcur.execute('SELECT id, name FROM Files WHERE nadded=-1 ORDER BY dtstr')
# Could do many files with:  for row in dbcur:
row = dbcur.fetchone()
if row == None:
    print("Nothing further to ingest.\n")
    quit()
print("Will ingest Jobs from file: "+row[1]+' [id='+str(row[0])+']\n')
file_id = row[0]
# set the number of days this file is since the previous file.
# Usually 1 day, some are missing so next ones are 2 days:
#  - no valid 2017-11-24
#  - no valid 2017-12-26 (files is _B: second 100 jobs)
# Could figure this out using dates in the database, since missing files
# are rare we'll hard-code those cases here.
dayssince = 1
if row[1] == '2017-11-25_A.html':
    dayssince = 2
if row[1] == '2017-12-27_A.html':
    dayssince = 2

# get a list of dictionaries of job values from the file
jobs_dictlist = wyzhelp.get_jobs_info(dailydir+"/"+row[1])
# reverse the order
jobs_dictlist.reverse()
print("Found "+str(len(jobs_dictlist))+" jobs in the file.\n")

# Put the job info into the Jobs database from the dictionaries;
# show what's in there...
print("Examples of job info (oldest first):\n")
for i in range(5):
    print(jobs_dictlist[i],'\n')
# {'wyzsubj': 'Calculus',
#  'city': 'East Lansing', 'state': 'MI', 'zip': '48823',
#  'jobtext': 'I have a freshman at MSU struggling . . . ',
#  'wyzid': '4123176', 'grade': 'College',
#  'name': 'Sherri', 'postdate': '2017-11-16'}

# We're going through the reversed list, so the oldest is first
# Keep track of how many we add to the Jobs list
jobs_added = 0
for ijob in range(len(jobs_dictlist)):
    dajob = jobs_dictlist[ijob]
    # Big question: Is this job already in the database?
    # Look for its wyzid, if there: get the original file_id and dayson
    dbcur.execute('''SELECT file_id, dayson FROM Jobs
                        WHERE wyzid=?''', ( dajob['wyzid'], ) )
    jobrow = dbcur.fetchone()
    if jobrow == None:
        # Not there - add it to Jobs table with dayson = dayssince.
        #
        # Also, get/include lowinc from zips
        dbcur.execute('''SELECT lowinc FROM Zips
                            WHERE izip=?''', ( int(dajob['zip']), ) )
        ziprow = dbcur.fetchone()
        # Make sure the ZIP is there...
        # Some ZIPs are not in the IRS file, can confirm by doing, e.g.,
        # linux$ grep ",93107" IRS_2015_data/15zpallagi.csv
        if ziprow == None:
            print(" * * * Did not find "+dajob['zip']+" in Zips * * *\n")
            lowinc=None
        else:
            lowinc = ziprow[0]
        #
        dbcur.execute('''INSERT INTO Jobs
                        (file_id, lastfile_id, verified, dayson, zip, lowinc,
                            wyzid, wyzsubj, grade, name, jobtext)
                        VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (file_id, file_id, 0, dayssince, dajob['zip'], lowinc,
                            dajob['wyzid'], dajob['wyzsubj'], dajob['grade'],
                            dajob['name'], dajob['jobtext']) )
        jobs_added += 1
    else:
        # The job is already there, update lastfile_id and dayson:
        # jobrow[1] has current dayson, add dayssince
        dayson = dayssince + jobrow[1]
        dbcur.execute('''UPDATE Jobs SET lastfile_id=? , verified=? , dayson=?
                        WHERE wyzid=?''',
                        ( file_id, 0, dayson, dajob['wyzid'] ) )

# Will put the number of added jobs in the Files table along
# with the lo and hi wyzid values (jobs are in oldest-to-newest order).
wyzidlo = jobs_dictlist[0]['wyzid']
wyzidhi = jobs_dictlist[-1]['wyzid']
# Also calculate the increase in the wyzidhi value from
# the previous wyzidhi value:
if file_id > 1:
    dbcur.execute('''SELECT wyzidhi FROM Files
                        WHERE id=?''', ( file_id-1, ) )
    prevwyzhi = dbcur.fetchone()[0]
else:
    prevwyzhi = wyzidlo  # special case for first file
# If there were no new jobs, then the wyzidhi is not meaningful...
if jobs_added == 0:
    wyzidhi = prevwyzhi
# and now form the increase of total wyzant jobs:
wyzadded = wyzidhi - prevwyzhi

print("Added "+str(jobs_added)+" jobs; IDs from "+
            str(wyzidlo)+" to "+str(wyzidhi)+".")
print("Prev wyzidhi is "+str(prevwyzhi)+", wyzadded = "+str(wyzadded)+"\n")
dbcur.execute('''UPDATE Files SET nadded=? , wyzidlo=? ,
                wyzidhi = ? , wyzadded = ?
                WHERE id=? ''', ( jobs_added, wyzidlo,
                                wyzidhi, wyzadded, file_id ) )

# Flag jobs whose dayson value is "verified" because:
#  we last saw it on immediately previous file  i.e. lastfile_id == (file_id - 1)
#  (AND therefore we don't/didn't see it in this file)
#  AND we would see it if it was still there  i.e.  its wyzid > wyzidlo
dbcur.execute('''UPDATE Jobs SET verified=1
                    WHERE wyzid>? AND lastfile_id=?''',
                        ( wyzidlo, file_id-1) )

# all done
dbconn.commit()
dbcur.close()
