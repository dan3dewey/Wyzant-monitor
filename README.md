# Wyzant-monitor
Extract daily information about Wyzant tutoring jobs and populate an
sqlite database with the information.

### Background
As a tutor with Wyzant.com I can view a list of online tutor jobs
throughout the USA;
specifically tutoring requests made by students in my subject areas.
The list changes as new student requests are posted and as previously
posted ones are removed (because a tutor connection was made, usually.)
I save the list of the most recent 100 job posts each morning in a
date-coded html file. These files are ingested and populate/update
a Jobs database file.

By tracking a tutoring job request from the day it appears until it is
gone from the list, I determine how quickly each tutor job was accepted
and can then see how that time varies with parameters, e.g. with ZIP
code or tutoring subject. A second database table with ZIP code as the
primary key is used to include other data, currently, from the IRS Income
Tax Statistics for a recent year.

### Implementation
In the sqlite database I have three tables: one listing the daily files,
one for the cumulative list of jobs,
and one with information based on ZIP codes.
For this last one, I read in [IRS tax return data by ZIP code](https://www.irs.gov/statistics/soi-tax-stats-individual-income-tax-statistics-2015-zip-code-data-soi)
(2015, all States, includes AGI; put in IRS_2015_data/15zpallagi.csv)
which `ZIPload.py` reads and uses the numbers of returns in different
income ranges to create a number indicating the low-income level of a ZIP code
(roughly the fraction of incomes <$25k minus the fraction with incomes >$100k.)

Most of the code is straight forward and based on examples
from [Python for Everybody](https://www.py4e.com). One unique aspect is the routine
`get_jobs_info( )` in `wyzhelp.py`: the parsing of the html jobs list is
carried out with an explicit finite-state machine design to accomodate the
variability of each posted job's html fields, etc.

Using sqlitebrowser, the sqlite data can be exported as Jobs.csv and Files.csv;
these can be read into display software such as Tableau.
Snapshot(s) showing the results are
on [my Tableau Public page](https://public.tableau.com/profile/daniel.dewey#!/) .

### Daily workflow:
Steps 1 and 2 are all that are required to populate the Jobs database; 
having the ZIP codes in the database is sufficient for Tableau to do geomapping.

1) Each morning:
     Download html page of the most recent 100 WyzAnt jobs available in my subjects.
     Use "Save page as..." in Chrome to save to a file, `yyyy-mm-dd_A.html`, in the dir `WyzAntDaily_Data/` (an example dir with a few files is included here.)

2) Ingest the new html file(s) and update job information by running:
     `$ python WyzIngest.py`

The following step creates a word cloud from the job descriptions' text.

3) For word-cloud visualiztion run: `$ python WyzWord.py` .
             Output is written to gword.js ;
      open gword.htm in a browser to see the vizualization.

![Tutoring requests word-cloud](/images/WyzWord_gword_output.png)


### Further things to do:
- Make a WyzSummary.py to list useful stats from the Jobs db, possibly selecting ones I should apply for ;-)
- Add daystr to the Files table in wyzjobs.sqlite db
  (or do this in Tableau from the file's date):
       it would be a string code for the day-of-week the job was posted,
       i.e., the day before the html file's date
       (since the file is captured in the morning and most jobs are submitted the previous day/night).
