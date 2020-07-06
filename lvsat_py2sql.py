# Script for parsing historical orbital launch data into SQL statements

# Original data source are the following lists
# https://planet4589.org/space/log/launchlogy.txt and
# https://www.planet4589.org/space/log/satcat.txt
# both maintained by Jonathan C. McDowell.

# launchlogy.txt format:
# 000 Launch (international designation)
# 013 Launch Date (UTC)
# 034 COSPAR designation (payload)
# 055 Payload name (after launch)
# 086 Payload name (before launch)
# 112 SATCAT number (payload)
# 121 LV type and name
# 144 LV serial number
# 160 Launch site (incl. pad)
# 193 Outcome
# 198 Reference

# satcat.txt format:
# 000 SATCAT number
# 008 COSPAR designation
# 023 Official name
# 064 Secondary name or prelaunch name.
# 089 Owner/Operator
# 102 Launch Date (UTC)
# 114 Current Status
# 132 Date of Status
# 144 Date of orbit epoch
# 156 Orbit class
# 165 Orbit period, minutes
# 175 Perigee x Apogee x Inclination

# What's currently working? launchlogy.tx
# TODO satcat.txt

import sys
import os

filler = ""
f_month = ""

filepath = 'launchlogy.txt'
with open(filepath) as fp:
   line = fp.readline()
   cnt = 1
   while line:
       if line[22].strip()=='' : filler="0"
       if line[18:21] == "Jan" : f_month="-01-"
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
       if line[0:1].strip() != "" : 
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
