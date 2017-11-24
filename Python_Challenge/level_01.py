# -*- coding: utf-8 -*-
"""
Created on Sat Oct 22 22:27:23 2016

@author: mthoren
"""

# http://www.pythonchallenge.com/pc/def/0.html is the "warmup"
# Substitute 274877906944 for 0 in the URL, brings you here:
# http://www.pythonchallenge.com/pc/def/map.html
# Apply a character map indicated by the picture to the "map" in the URL to
# get "ocr", and voila! next URL.

# Trantab seems to crash Spyder now!!
dotrantab = False
if dotrantab == True:
    from string import maketrans
    intab  = "abcdefghijklmnopqrstuvwxyz"
    outtab = "cdefghijklmnopqrstuvwxyzab"
    print("Making trantab...")
    trantab = maketrans(intab, outtab)
    
    str = "this is string example....wow!!!"
<<<<<<< HEAD
    str = "g fmnc wms bgblr rpylqjyrc gr zw fylb. rfyrq ufyr amknsrcpq ypc dmp. bmgle gr gl zw fylb gq glcddgagclr ylb rfyr'q ufw rfgq rcvr gq qm jmle. sqgle qrpgle.kyicrpylq() gq pcamkkclbcb. lmu ynnjw ml rfc spj"
    print (str)
    print("\n")
    print str.translate(trantab)
    print("\n")
    print("A-Ha! Now apply on the url, map\n")
    print "map".translate(trantab)
    print("\n")
=======
    
    str = "g fmnc wms bgblr rpylqjyrc gr zw fylb. rfyrq ufyr amknsrcpq ypc dmp. bmgle gr gl zw fylb gq glcddgagclr ylb rfyr'q ufw rfgq rcvr gq qm jmle. sqgle qrpgle.kyicrpylq() gq pcamkkclbcb. lmu ynnjw ml rfc spj"
    print (str)
    print str.translate(trantab)
>>>>>>> remotes/origin/init_cleanup


with open("ocr_string.txt") as f:
    content = f.readlines()

print("Done reading ocr_string!")

print("Here we go with ocr challenge!")
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
           eq_data[row][ch+4].islower() #and # D'oh!! I over-interpreted.
#           eq_data[row-4][ch].islower() and # Turns out we're only looing
#           eq_data[row-3][ch].isupper() and # for right / left, not top / bot.
#           eq_data[row-2][ch].isupper() and
#           eq_data[row-1][ch].isupper() and
#           eq_data[row+1][ch].isupper() and
#           eq_data[row+2][ch].isupper() and
#           eq_data[row+3][ch].isupper() and
#           eq_data[row+4][ch].islower()
           
           ):
            #print ("row: " + str(row) + "col: " + str(ch) + "ch: " + str(eq_data[row][ch]))
            print eq_data[row][ch]
            
for row in range(0, rows):
    if eq_data[row].strip().isalpha() == False:
        print("row " + str(row) + "has nonalpha")