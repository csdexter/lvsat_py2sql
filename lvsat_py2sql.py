import sys
import os

filler = ""
f_month = ""

filepath = 'launchlogy.txt'

with open(filepath) as fp:
   line = fp.readline()
   line = fp.readline()
   line = fp.readline()                             # dirty way of starting to read the file from its third line
   cnt = 1
   
   while line:
       if line[22].strip()=='' : filler="0"         # converting single-digit day number to two-digit, by adding a leading 0
       if line[18:21] == "Jan" : f_month="-01-"     # converting dates to timestamp format accepted by PostgreSQL 
       if line[18:21] == "Feb" : f_month="-02-"
       if line[18:21] == "Mar" : f_month="-03-"
       if line[18:21] == "Apr" : f_month="-04-"
       if line[18:21] == "May" : f_month="-05-"
       if line[18:21] == "Jun" : f_month="-06-"
       if line[18:21] == "Jul" : f_month="-07-"
       if line[18:21] == "Aug" : f_month="-08-"
       if line[18:21] == "Sep" : f_month="-09-"
       if line[18:21] == "Oct" : f_month="-10-"
       if line[18:21] == "Nov" : f_month="-11-"
       if line[18:21] == "Dec" : f_month="-12-"
       
       if line[0:1].strip() != "" :                 # skipping the lines dealing only with payloads (treated differently)
           print("INSERT INTO launches VALUES ('"+line[0:10].strip()
                   +"','"+line[13:18].strip()+f_month+line[22:23].strip()+filler+line[23:27]+":"+line[27:29]
                   +"','"+line[40:55].strip()
                   +"','"+line[55:86].strip()
                   +"','"+line[86:112].strip()
                   +"','"+line[112:121].strip()
                   +"','"+line[121:144].strip()
                   +"','"+line[144:160].strip()
                   +"','"+line[160:193].strip()
                   +"','"+line[193:194].strip()
                   +"')")
       
       filler = ""
       f_month=""
       line = fp.readline()
       cnt += 1
