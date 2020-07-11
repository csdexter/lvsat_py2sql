import sys
import os

def db_reinit():
    print("DROP TABLE satellites;")
    print("DROP TABLE launches;")

    print("CREATE TABLE launches (")
    print("launchID TEXT,")
    print("launchDate TIMESTAMP,")
    print("COSPAR TEXT,")
    print("postPayload TEXT,")
    print("prePayload TEXT,")
    print("SATCAT TEXT,")
    print("LV_type TEXT,")
    print("LV_serial TEXT,")
    print("launchSite TEXT,")
    print("launchPad TEXT,")
    print("lsState TEXT,")
    print("outcome TEXT")
    print(");")

    print("CREATE TABLE satellites (")
    print("launchID TEXT,")
    print("COSPAR TEXT,")
    print("postPayload TEXT,")
    print("prePayload TEXT,")
    print("owner TEXT,")
    print("SATCAT TEXT,")
    print("orbitPrd TEXT,")
    print("orbitClass TEXT,")
    print("orbitPAI TEXT")
    print(");")

filler = ""
f_month = ""
lsState = ""
match = 0

filepath_lv = 'launchlogy.txt'
filepath_sat = 'satcat.txt'
filepath_site = 'sites.txt'

if (len(sys.argv) == 2) and (sys.argv[1] == "--reinit"):
    db_reinit()

if len(sys.argv) !=2: pass

with open(filepath_sat) as sat_file:                                            # the content of "satcat.txt" is stored in sat_array[]
    sat_array = sat_file.readlines()

with open(filepath_site, encoding="utf8") as site_file:                         # the content of "sites.txt" is stored in sat_array[]
    site_array = site_file.readlines()

with open(filepath_lv) as fp:                                                   # "launchlogy.txt" is not stored, it's processed as it's read
    line_lv = fp.readline()
    line_lv = fp.readline()
    line_lv = fp.readline()                                                     # dirty way of starting to read the file from its third line
    cnt = 1

    while line_lv:
        if line_lv[22].strip()=='' : filler="0"                                 # converting single-digit day number to two-digit, by adding a leading 0
        if line_lv[18:21] == "Jan" : f_month="-01-"                             # converting dates to timestamp format accepted by PostgreSQL
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

        for y in range(len(site_array)):
            if site_array[y][0:9].strip()==(line_lv[160:169].strip()):
                lsState = site_array[y][40:49].strip()
                lsName = site_array[y][93:174].strip().replace("'","''")

        if line_lv[0:1].strip() != "" :                                         # skipping the lines dealing only with payloads (treated separately)
            launchID = line_lv[0:10].strip()
            print("INSERT INTO launches VALUES ('"+launchID                     # launchID
                +"','"+line_lv[13:18].strip()+f_month                           # launchDate
                +line_lv[22:23].strip()+filler
                +line_lv[23:27]+":"+line_lv[27:29]
                +"','"+line_lv[40:55].strip()                                   # COSPAR
                +"','"+line_lv[55:86].strip().replace("'","''")                 # postPayload | for launches table, only the first payload is mentioned
                +"','"+line_lv[86:112].strip().replace("'","''")                # prePayload  | for the full payload configuration, see satellited table
                +"','"+line_lv[112:121].strip()                                 # SATCAT
                +"','"+line_lv[121:144].strip()                                 # LV_type
                +"','"+line_lv[144:160].strip()                                 # LV_serial
                +"','"+lsName                                                   # launchSite
                +"','"+line_lv[169:193].strip()                                 # launchPad
                +"','"+lsState                                                  # lsState
                +"','"+line_lv[193:194].strip()                                 # outcome
                +"');")

            for x in range(len(sat_array)):                         	        # looking for a match in satcat.txt
                if sat_array[x][0:8].strip()==("S0"+line_lv[113:120].strip()):  # SATCAT have an extra 0 digit in satcat.txt
                    match = x

            print("INSERT INTO satellites VALUES ('"+launchID                   # launchID
                +"','"+line_lv[40:55].strip()                                   # COSPAR
                +"','"+line_lv[55:86].strip().replace("'","''")                 # postPayload
                +"','"+line_lv[86:112].strip().replace("'","''")                # prePayload
                +"','"+sat_array[match][89:102].strip()                         # owner
                +"','"+line_lv[112:121].strip()                                 # SATCAT
                +"','"+sat_array[match][166:175].strip()                        # orbitPrd
                +"','"+sat_array[match][156:167].strip()                        # orbitClass
                +"','"+sat_array[match][177:198].replace(" ", "")               # orbitPAI
                +"');")

        else:

            print("INSERT INTO satellites VALUES ('"+launchID                   # launchID
                +"','"+line_lv[40:55].strip()                                   # COSPAR
                +"','"+line_lv[55:86].strip().replace("'","''")                 # postPayload
                +"','"+line_lv[86:112].strip().replace("Ven{\\mu}s", "Venmus").replace("'","''")  # prePayload, dealing with apostrophes and a LaTeX relic(?)
                +"','"+sat_array[match][89:102].strip()                         # owner
                +"','"+line_lv[112:121].strip()                                 # SATCAT
                +"','"+sat_array[match][166:175].strip()                        # orbitPrd
                +"','"+sat_array[match][156:167].strip()                        # orbitClass
                +"','"+sat_array[match][177:198].replace(" ", "")               # orbitPAI
                +"');")

        filler = ""
        f_month = ""
        line_lv = fp.readline()
        cnt += 1
