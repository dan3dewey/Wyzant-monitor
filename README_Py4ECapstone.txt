file: README_Py4ECapstone.txt     12/12/2017

1) Each morning:
     Download html page of 100 WyzAnt jobs,
     put into file <datecode>_A.html in WyzAnt_Daily/

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

- - - 
Just the Daily Data:
tar -cvf WyzDaily.tar WyzAntDaily_Data/*_A.html
gzip WyzDaily.tar


