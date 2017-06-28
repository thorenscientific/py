# -*- coding: utf-8 -*-
"""
Created on Sat Nov 05 16:30:05 2016

@author: mthoren

URL summary:
Level 00 http://www.pythonchallenge.com/pc/def/0.html
Level 01 http://www.pythonchallenge.com/pc/def/map.html
Level 02 http://www.pythonchallenge.com/pc/def/ocr.html
Level 03 http://www.pythonchallenge.com/pc/def/equality.html

Level 05 http://www.pythonchallenge.com/pc/def/peak.html
Level 06 http://www.pythonchallenge.com/pc/def/channel.html





"""
print("Here we go!")
# http://www.pythonchallenge.com/pc/def/0.html
# Warmup, photo with 2^38 in it. Change URL to:
# http://www.pythonchallenge.com/pc/def/274877906944.html
# brings us to:
# http://www.pythonchallenge.com/pc/def/map.html
# Photo of a piece of paper, K -> M, O -> Q, E -> G
# which is a hint to map each letter to two letters ahead...

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
# http://www.pythonchallenge.com/pc/def/linkedlist.html

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
# http://www.pythonchallenge.com/pc/def/peak.html
    
# Viewing source, gives us a hint: <peakhell src="banner.p"/> so we go to...
# http://www.pythonchallenge.com/pc/def/banner.p
# which is a bunch of gibberish ending with a period, so it must be a pickle...
    
import pickle

f = urllib.urlopen("http://www.pythonchallenge.com/pc/def/banner.p")
mypickle = f.read()
answer = pickle.loads(mypickle)
print("Pickle answer...")
print answer
print("Yuck, let's print element by element to see if we can detect a pattern...")
for i in range(0,len(answer)):
    print(answer[i])
print("Done! Well, nothing obvious yet... how about the number of elements?:")
for i in range(0,len(answer)):
    print(len(answer[i]))

# A-ha! I think i see what's going on. Print the character the number of times
# indicated...
for i in range(0,len(answer)):
    mystr = ""
    for j in range(0, len(answer[i])):
        for numch in range(0, answer[i][j][1]):
            mystr += answer[i][j][0]
    print(mystr)
# WooHoo! It prints out "channel"!
# Let's go to...
# http://www.pythonchallenge.com/pc/def/channel.html
# Nice pic of a zipper, PayPal donation buttion... let's get going!
# What the heck, let's go here:
# http://www.pythonchallenge.com/pc/def/zipper.html
# Which gives us this hint (and no further hints in source):
# [:3] todo: tell everyone that [:n] is to take the first n characters...
# http://www.pythonchallenge.com/pc/def/zip.html
# tells us "yes, find the zip."  
    
    
    




