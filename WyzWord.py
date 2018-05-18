# file: WyzWord.py  copied/modified from Py4E gword.py

import sqlite3
import time
import string

# Open the WyzAnt Jobs database
conn = sqlite3.connect('wyzjobs.sqlite')
cur = conn.cursor()

# Go through the jobtext values and count words in each (count repeat words)
#
# Get all of the jobs text:
grade = ''
#   or
# Specify the 'grade':
#grade = "Middle school"
#grade = 'High school'
#grade = 'College'
#grade = 'Adult'
#grade = "(Not Given)"

if grade == '':
    cur.execute('SELECT jobtext FROM Jobs' )
else:
    cur.execute('SELECT jobtext FROM Jobs WHERE grade=?' , (grade,) )
counts = dict()
for row in cur :
    text = row[0]
    # get rid of punctuation and numbers
    text = text.translate(str.maketrans('','',string.punctuation))
    text = text.translate(str.maketrans('','','1234567890'))
    text = text.strip()
    text = text.lower()
    words = text.split()
    # Only count 4 or more lettered words
    for word in words:
        # Remove some uninteresting words
        # (In order to leave "I", "my", "son", etc. for examples)
        if word in 'am as at bc be do hs if ii in it no of on pm to up':
            continue
        elif (word in 'all and are but can dec few for get has job not now' +
                    ' old one our out sat the two was who'):
            continue
        elif (word in 'also ampm been both exam from good have high just last like more next once over'+
                ' right some text that then this very want week well will with year'):
            continue
        elif (word in 'about after coming could currently going having school'+
                ' someone three which would'):
            continue
        elif word in 'monday tuesday wednesday thursday friday saturday sunday':
            continue
        # And make some adjustments
        if (word == 'needs' or word == 'needing'):
            word = 'need'
        elif word == 'calc':
            word = 'calculus'
        elif word == 'times': word = 'time'
        elif (word == 'precal' or word == 'precalc'):
            word = 'precalculus'
        # Some CAPITALS added (start the if over)
        if (word == 'im' or word == "i'm" or word == "i’m"):
            word = "I"
        elif word == 'ap': word = 'AP'
        elif word == 'math': word = 'Math'
        elif word == 'physics': word = 'Physics'
        elif word == 'algebra': word = 'Algebra'
        elif word == 'geometry': word = 'Geometry'
        elif word == 'precalculus': word = 'Precalculus'
        elif word == 'calculus': word = 'Calculus'

        counts[word] = counts.get(word,0) + 1

x = sorted(counts, key=counts.get, reverse=True)
highest = None
lowest = None

number_in_cloud = 80

for k in x[:number_in_cloud]:
    if highest is None or highest < counts[k] :
        highest = counts[k]
    if lowest is None or lowest > counts[k] :
        lowest = counts[k]
print('Range of counts:',highest,lowest)

# Spread the font sizes across 20-100 based on the count
bigsize = 80
smallsize = 20

fhand = open('gword.js','w')
fhand.write("gword = [")
first = True
for k in x[:number_in_cloud]:
    if not first : fhand.write( ",\n")
    first = False
    size = counts[k]
    size = (size - lowest) / float(highest - lowest)
    size = int((size * bigsize) + smallsize)
    fhand.write("{text: '"+k+"', size: "+str(size)+"}")
fhand.write( "\n];\n")
fhand.close()

print("Output written to gword.js")
print("Open gword.htm in a browser to see the vizualization")
