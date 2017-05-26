# -*- coding: utf-8 -*-
"""
Created on Sat Nov 05 16:30:05 2016

@author: mthoren
"""
print("Here we go!")
for line in open("ocr.txt"):
    for ch in line:
        if ch in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
            print(ch)

eq_data = [] # Init array

print("loading equality challenge text!")
for line in open("equality.txt"):
    eq_data.append(line)

rows = len(eq_data)

for row in range(3, rows - 4):
    for ch in range(4, len(eq_data[row])-4):
        if(eq_data[row][ch].islower() and
           eq_data[row][ch-4].islower()and
           eq_data[row][ch-3].isupper()and
           eq_data[row][ch-2].isupper() and
           eq_data[row][ch-1].isupper() and 
           eq_data[row][ch+1].isupper() and
           eq_data[row][ch+2].isupper() and
           eq_data[row][ch+3].isupper() and
           eq_data[row][ch+4].islower() #and
#           eq_data[row-4][ch].islower() and
#           eq_data[row-3][ch].isupper() and
#           eq_data[row-2][ch].isupper() and
#           eq_data[row-1][ch].isupper() and
#           eq_data[row+1][ch].isupper() and
#           eq_data[row+2][ch].isupper() and
#           eq_data[row+3][ch].isupper() and
#           eq_data[row+4][ch].islower()
           
           ):
            print ("row: " + str(row) + "col: " + str(ch) + "ch: " + str(eq_data[row][ch]))
            #print eq_data[row][ch]
            
for row in range(0, rows):
    if eq_data[row].strip().isalpha() == False:
        print("row " + str(row) + "has nonalpha")
        
# And with that, we get the text "linkedlist", which gives us our next URL!

import urllib
RunLinkedList = False
if RunLinkedList == True:
    nextnum = "12345"
    for i in range (0, 400):
        f = urllib.urlopen("http://www.pythonchallenge.com/pc/def/linkedlist.php?nothing=" + nextnum)
        mystr = f.read()
        words = mystr.split()
        nextnum = words[len(words)-1]
        print (mystr)
    
# Ha! This gives us "Yes. Divide by two and keep going." at one point, 
# and finally, somewhere along the line, "peak.html" which leads to the next challenge!
import pickle

f = urllib.urlopen("http://www.pythonchallenge.com/pc/def/banner.p")
mypickle = f.read()
answer = pickle.loads(mypickle)
print("Pickle answer...")
print answer


