import sys
import os

filler = ""
f_month = ""

filepath_lv = 'launchlogy.txt'
filepath_sat = 'satcat.txt'

with open(filepath_sat) as sat_file:                       # the content of satcat.txt is stored in sat_array[]
    sat_array = sat_file.readlines()

numrows = len(sat_array)
numcols = len(sat_array[0])

match = 0

with open(filepath_lv) as fp:
       line_lv = fp.readline()
       line_lv = fp.readline()
       line_lv = fp.readline()                             # dirty way of starting to read the file from its third line
       cnt = 1

       while line_lv:
           if line_lv[22].strip()=='' : filler="0"         # converting single-digit day number to two-digit, by adding a leading 0
           if line_lv[18:21] == "Jan" : f_month="-01-"     # converting dates to timestamp format accepted by PostgreSQL
           if line_lv[18:21] == "Feb" : f_month="-02-"
           if line_lv[18:21] == "Mar" : f_month="-03-"
           if line_lv[18:21] == "Apr" : f_month="-04-"
           if line_lv[18:21] == "May" : f_month="-05-"
           if line_lv[18:21] == "Jun" : f_month="-06-"
           if line_lv[18:21] == "Jul" : f_month="-07-"
           if line_lv[18:21] == "Aug" : f_month="-08-"
           if line_lv[18:21] == "Sep" : f_month="-09-"
           if line_lv[18:21] == "Oct" : f_month="-10-"
           if line_lv[18:21] == "Nov" : f_month="-11-"
           if line_lv[18:21] == "Dec" : f_month="-12-"

           if line_lv[0:1].strip() != "" :                 # skipping the lines dealing only with payloads (treated differently)
               launchID = line_lv[0:10].strip()
               print("INSERT INTO launches VALUES ('"+launchID
                       +"','"+line_lv[13:18].strip()+f_month+line_lv[22:23].strip()+filler+line_lv[23:27]+":"+line_lv[27:29]
                       +"','"+line_lv[40:55].strip()
                       +"','"+line_lv[55:86].strip()
                       +"','"+line_lv[86:112].strip()
                       +"','"+line_lv[112:121].strip()
                       +"','"+line_lv[121:144].strip()
                       +"','"+line_lv[144:160].strip()
                       +"','"+line_lv[160:193].strip()
                       +"','"+line_lv[193:194].strip()
                       +"')")

               for x in range(len(sat_array)):
                   if (sat_array[x][0:8].strip()) == ("S0"+line_lv[113:120].strip()):
                       match = x

               print("INSERT INTO satellites VALUES ('"+launchID
                       +"','"+line_lv[40:55].strip()
                       +"','"+line_lv[55:86].strip()
                       +"','"+line_lv[86:112].strip()
                       +"','"+line_lv[112:121].strip()
                       +"','"+sat_array[match][156:167].strip()
                       +"','"+sat_array[match][177:198].strip()
                       +"')")
           else:
               print("INSERT INTO satellites VALUES ('"+launchID
                       +"','"+line_lv[40:55].strip()
                       +"','"+line_lv[55:86].strip()
                       +"','"+line_lv[86:112].strip()
                       +"','"+line_lv[112:121].strip()
                       +"','"+sat_array[match][156:167].strip()
                       +"','"+sat_array[match][177:198].strip()
                       +"')")

           filler = ""
           f_month=""
           line_lv = fp.readline()
           cnt += 1
