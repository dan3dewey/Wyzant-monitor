# Wyzant-monitor
Extract daily information about Wyzant tutoring jobs and populate an sqlite database with the information.

# Background
As a tutor with WyzAnt.com I can view a list of online tutor jobs throughout the USA;
specifically tutoring requests made by students in my subject areas.
The list changes as new student requests are posted and as previously posted ones are removed
(because a tutor connection was made, usually.) I save the list of the most recent 100 job posts
each morning in a date-coded html file. These files are ingested (each day) and populate/update
a Jobs database file.

By tracking a tutoring job request from the day it appears until it is gone from the list,
I determine how quickly each tutor job was accepted and can then see how that time varies with parameters,
e.g. with ZIP code or tutoring subject. A second database table with ZIP code as the primary key
can be used to include other data, for example, from the IRS Income Tax Statistics for a recent year.

In the sqlite database I have three tables: one listing the daily files, one for the cumulative list of jobs,
and one with information based on ZIP codes.  For this last one, I read in IRS tax return data by ZIP code ( https://www.irs.go/statistics/soi-tax-stats-individual-income-tax-statistics-2015-zip-code-data-soi )
and used the numbers of returns in different income ranges to create a number indicating the
low-income level of a ZIP code (roughly the fraction of incomes <$25k minus the fraction with incomes >$100k.)

The sqlite data can be exported from sqlitebrowser as csv files and read into display software such as Tableau.

# Daily workflow:
Steps 1 and 2 are all that are required to populate the Jobs database; 
the ZIP codes in the database are sufficient for Tableau to do geomapping.

1) Each morning:
     Download html page of most recent 100 WyzAnt jobs.
     Use "Save page as..." in Chrome to create a file <datecode>_A.html in dir WyzAnt_Daily/

2) linux$ python WyzIngest.py

These steps create a word cloud from job descriptions and get further geodata from the ZIP codes
(i.e., lat and long) to create a geomap.

3) For word-cloud visualiztion run: linux$ python WyzWord.py ;
             Output is written to gword.js ;
   Open gword.htm in a browser to see the vizualization.

4) For a geographic map of locations run: linux$ python WyzGeo.py ;
         makes a where_wyz.data file with each line containing
              "<zipcode>, USA" ;
   run linux$ python geoload_wyz.py
                                 to go through where_wyz.data and use Google (100 per day limit)
                                 to get geodata for ZIP codes and save it in geodata_wyz.sqlite.
   Running linux$ python geodump_wyz.py generates a where.js file
   which is used when viewing where_dd.html in a browser.


# Further things to do:
- Make WyzSummary.py to list useful stats from the Jobs db.
- Add daystr to the Files table in wyzjobs.sqlite db:
       it is 3 character string code for the day the job was posted,
       i.e., the day before the file date
       (since file is captured in the morning and most jobs are submitted the previous day/night).


# Making tar files to save/backup stuff:
Use of github will make this unnecessary... Save the code and this file:

tar -cvf WyzPython.tar *.py READ*.txt
gzip WyzPython.tar

Save the raw Data and databases:  (not IRS or ZIPs, include csvs)

tar -cvf WyzData.tar *wyz*.sqlite *.csv WyzAntDaily_Data/*_A.html
gzip WyzData.tar

