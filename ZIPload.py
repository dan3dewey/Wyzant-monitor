# file: ZIPload.py
import sqlite3
import re
import numpy as np

# Fill the ZIP database table with values
# - - - Open the database - - -
dbconn = sqlite3.connect('wyzjobs.sqlite')
dbcur = dbconn.cursor()
# Define the Zips table - we'll reform it each time this is run
dbcur.execute('DROP TABLE IF EXISTS Zips')
dbcur.execute('''CREATE TABLE IF NOT EXISTS Zips
                (izip INTEGER PRIMARY KEY, popul INTEGER, lowinc REAL )''')

# Reading in IRS income tax data by ZIP code, with breakdown by AGI:
# agi_stub
#   1  < 25k
#   2  < 50k
#   3  < 75k
#   4  < 100k
#   5  < 200k
#   6  >= 200k
# File format is header line and then six lines per zip:
#  STATEFIPS,STATE,zipcode,agi_stub,N1,
#  36,NY,10308,1,3820.0000, . . .
# . . .
#  36,NY,10308,6,720.0000, . . .

# Read the file and save the N1 (number) in an array of size 100000 by 6
zip_data = np.zeros(100000*6).reshape(100000,6)

get_header = True
line_count = 0
# 166681 is number of lines in the file = 27780 * 6 + 1
max_lines = 180000

fzip = open('IRS_2015_data/15zpallagi.csv','r')
for line in fzip:
    if get_header:
        header = line
        get_header = False
        continue
    # get the start of the line, minus statefips
    stuff = re.findall('^\S\S,\S\S,(\S\S\S\S\S,\S,[0-9]+?.0)000,', line)
    line_count += 1
    if line_count > max_lines: break
    pieces = stuff[0].split(',')
    zipint = int(pieces[0])
    agiint = int(pieces[1])-1  # 0 to 5
    zip_data[zipint][agiint] = float(pieces[2])

# show the last line read in and the array format
print(line)
print(zip_data)
fzip.close()

# Get total N1 (~ population who filed)
# and make zip_data be fractions
zippop = np.zeros(100000)
# Define a low-income indicator = agi_1 - (agi_5+agi_6)
lowinc = np.zeros(100000)
for izip in range(100000):
    zippop[izip] = sum(zip_data[izip])
    if zippop[izip] > 0:
        zip_data[izip] /= zippop[izip]
    lowinc[izip] = np.dot(zip_data[izip],np.array([1.,0.,0.,0.,-1.,-1.]))

# Show these values for places I've lived ;-)
print(zippop[1602],lowinc[1602],zip_data[1602])
print(zippop[2139],lowinc[2139],zip_data[2139])
print(zippop[2140],lowinc[2140],zip_data[2140])
print(zippop[1373],lowinc[1373],zip_data[1373])
print(zippop[1040],lowinc[1040],zip_data[1040])


# Load in the zips with non-zero population, and their lowinc value
for i in range(1,99998):
    if zippop[i] > 0:
        dbcur.execute('''INSERT INTO Zips (izip, popul, lowinc)
                        VALUES ( ? , ? , ? )''',
                        ( i, int(zippop[i]), lowinc[i] ) )
        #print("Inserting: ",i, " ", int(zippop[i]), " ", lowinc[i])

dbconn.commit()
dbcur.close()
