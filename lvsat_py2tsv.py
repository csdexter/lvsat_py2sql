# experimental, do not touch

import sys
import os

filler = ""
f_month = ""
lsState = ""
match = 0

filepath_lv = 'launchlog.txt'
filepath_sat = 'satcat.txt'
filepath_site = 'sites.txt'
output = 'output.tsv'

with open(output, 'w') as f:
    f.write("")

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
                if lsState == "J" : lsState = "JP"                              # lsState
#                lsName = site_array[y][0:9].strip()                             # launchSite

        if line_lv[0:1].strip() != "" :                                         # skipping the lines dealing only with payloads (treated separately)
            lv_launchID = line_lv[0:10].strip()                                 # launchID
            lv_launchDate = line_lv[13:18].strip()+f_month+line_lv[22:23].strip()+filler+line_lv[23:27]+":"+line_lv[27:29]
            if line_lv[27:29].strip() == "" : lv_launchDate = line_lv[13:18].strip()+f_month+line_lv[22:24].strip()+filler+line_lv[23:27]
            if line_lv[25:27].strip() == "" : lv_launchDate = line_lv[13:18].strip()+f_month+line_lv[22:24].strip()+filler
            lv_COSPAR = line_lv[40:55].strip()                                  # COSPAR
            lv_postpayload = line_lv[55:86].strip()                             # postPayload | for launches table, only the first payload is mentioned
            lv_prepayload = line_lv[86:112].strip()                             # prePayload  | for the full payload configuration, see satellited table
            lv_SATCAT = line_lv[112:121].strip()                                # SATCAT
            lv_type = line_lv[121:144].strip()                                  # LV_type
            if lv_type == "Soyuz-2-1A": lv_type = "Soyuz-2.1a"
            if lv_type == "Soyuz-2-1B": lv_type = "Soyuz-2.1b"
            if lv_type == "Falcon 9"  : lv_type = "Falcon-9"
            lv_serial = line_lv[144:160].strip()                                # LV_serial
            lsName = line_lv[160:169].strip()                                   # launchSite
            lv_launchPad = line_lv[169:193].strip()                             # launchPad
            lv_outcome = line_lv[193:194].strip()                               # outcome

            for x in range(len(sat_array)):                         	        # looking for a match in satcat.txt
                if sat_array[x][0:8].strip()==("S0"+line_lv[113:120].strip()):  # SATCAT have an extra 0 digit in satcat.txt
                    match = x

            sat_owner = sat_array[match][89:102].strip()                        # owner
#           sat_orbitPrd = sat_array[match][166:175].strip()                    # orbitPrd
            sat_orbitClass = sat_array[match][156:165].strip()                  # orbitClass
#           sat_orbitPAI = sat_array[match][177:198]                            # orbitPAI

            sys.stdout.write("processing year: "+lv_launchDate[0:4]+"; entry: "+str(cnt)+"\r")

            with open(output, 'a') as f:
                f.write(lv_launchID.ljust(12) + lv_launchDate.ljust(18) + lv_type.ljust(23) + lv_serial.ljust(20) + lv_prepayload.ljust(30) + lv_postpayload.ljust(30) + sat_owner.ljust(14) + sat_orbitClass.ljust(10) + lsState.ljust(5) + lsName.ljust(9) + lv_launchPad.ljust(25) + lv_outcome.ljust(2) + "\n")

        else: pass

        filler = ""
        f_month = ""
        line_lv = fp.readline()
        cnt += 1
