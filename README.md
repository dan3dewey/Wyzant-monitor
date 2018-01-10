# Wyzant-monitor
Extract daily information about Wyzant tutoring jobs and populate an sqlite database with the information.

# Background
I'm a tutor through WyzAnt.com (in-person and online) and I can view a list of online tutor jobs throughout the U
SA; these are tutoring requests made by students in my subject areas.  The list changes as new student requests a
re posted and as previously posted ones are removed (because a tutor connection was made, usually.) For my main d
ata source I'm saving the list of the most recent 100 job posts each morning, as an html file named with the date
. These will be ingested (each day) into a "job requests" database table.

By tracking a tutoring request from the day it appears until it is gone from the list, I can determine how quickl
y each tutor job was accepted and see how that time varies with parameters, e.g. with ZIP code or tutoring subjec
t. I can then also have a second database table with the ZIP code as the primary key and include other by-ZIP-cod
e data, for example some of the IRS Income Tax Statistics for a recent year, and see if/how that relates to the t
utor acceptance time.

In the sqlite database I have three tables: one for the daily files, one for the cumula
tive list of jobs, and one with information based on ZIP codes.  For this last one,
I read in IRS tax return data by ZIP code (https://www.irs.go/statistics/soi-tax-stats-individual-income-ta
x-statistics-2015-zip-code-data-soi) and used the numbers of returns in different income ranges to create a numbe
r indicating the low-income level of a ZIP code (roughly the fraction of incomes <$25k minus the fraction with incomes >$100k
.)

# Daily workflow:
1) Each morning:
     Download html page of most recent 100 WyzAnt jobs,
     "Save page as..." into file <datecode>_A.html in WyzAnt_Daily/

2) linux$ python WyzIngest.py

3) linux$ python WyzWord.py
             Output written to gword.js
   Open gword.htm in a browser to see the vizualization

4) linux$ python WyzGeo.py
         Makes a where_wyz.data file with each line:
              <zipcode>, USA
   linux$ python geoload_wyz.py
                                 takes where_wyz.data, adds to geodata_wyz.sqlite
                                 using Google (100 per day limit.)
   linux$ python geodump_wyz.py
                                 generates a where.js file
   Open where_dd.html to view the data in a browser


- - - Further things to do:
- Make WyzSummary.py to list useful stats from the Jobs db.
- Have WyzGeo.py output only selected locations,
  e.g., all verified 1-days, all >6 days
  to a where_wyz<Filtered>.data file
          [copy it to where_wyz.data to continue and view] 
- Modify geodump_wyz.py to only output locs in where_wyz.data (not whole db);
       include duplicates with some random lat, long.
- Add daystr to the Files table in wyzjobs.sqlite db:
       it is string code for the day job was posted,
       i.e., the day before the file date
       (since file captured in morning and most jobs submitted previous day/night)


- - - Making tar files to save/backup stuff:
Code and this file:

tar -cvf WyzPython.tar *.py READ*.txt
gzip WyzPython.tar

My Data:  (not IRS or ZIPs, include csvs)

tar -cvf WyzData.tar *wyz*.sqlite *.csv WyzAntDaily_Data/*_A.html
gzip WyzData.tar

