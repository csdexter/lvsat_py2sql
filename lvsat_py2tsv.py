# experimental, do not touch

import sys
import os
import time

tic = time.perf_counter()

filler = ""
f_month = ""
lsState = ""
match = 0

filepath_lv = 'launchlog.txt'
filepath_sat = 'satcat.txt'
filepath_site = 'sites.txt'
output = 'output.txt'

with open(output, 'w') as f:
    f.write("")

# the content of "satcat.txt" is stored in sat_array[]
with open(filepath_sat) as sat_file:
    sat_array = sat_file.readlines()

# the content of "sites.txt" is stored in sat_array[]
with open(filepath_site, encoding="utf8") as site_file:
    site_array = site_file.readlines()

# "launchlogy.txt" is not stored, it's processed as it's read
with open(filepath_lv) as fp:
    # dirty way of starting to read the file from its third line
    line_lv = fp.readline()
    line_lv = fp.readline()
    line_lv = fp.readline()
    cnt = 1

    while line_lv:
        # converting single-digit day number to two-digit, by adding a leading 0
        if line_lv[22].strip()=='' : filler="0"
        # converting dates to timestamp format accepted by PostgreSQL
        if line_lv[18:21] == "Jan" : f_month="-01-"
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

        # collecting data from sites.txt, namely lsState variable
        for y in range(len(site_array)):
            if site_array[y][0:9].strip()==(line_lv[160:169].strip()):
                ls_state = site_array[y][40:49].strip()

                # prettifying record for Japan
                if ls_state == "J" : ls_state = "JP"

        # skipping the lines dealing only with payloads (we're interested in launches, not satellites)
        # and processing launchlog.txt
        if line_lv[0:1].strip() != "" :
            lv_launchID = line_lv[0:10].strip()
            lv_launchDate = line_lv[13:18].strip()+f_month+line_lv[22:23].strip()+filler+line_lv[23:27]+":"+line_lv[27:29]

            # dealing with incomplete date records
            if line_lv[27:29].strip() == "" : lv_launchDate = line_lv[13:18].strip()+f_month+line_lv[22:24].strip()+filler+line_lv[23:27]
            if line_lv[25:27].strip() == "" : lv_launchDate = line_lv[13:18].strip()+f_month+line_lv[22:24].strip()+filler

            lv_COSPAR = line_lv[40:55].strip()
            lv_postPayload = line_lv[55:86].strip()
            lv_prePayload = line_lv[86:112].strip()
            lv_SATCAT = line_lv[112:121].strip()
            lv_type = line_lv[121:144].strip()

            # adjusting the names of some rockets
            if lv_type == "Soyuz-2-1A": lv_type = "Soyuz-2.1a"
            if lv_type == "Soyuz-2-1B": lv_type = "Soyuz-2.1b"
            if lv_type == "Soyuz-2-1V": lv_type = "Soyuz-2.1v"
            if lv_type == "Falcon 9"  : lv_type = "Falcon-9"

            lv_serial = line_lv[144:160].strip()
            ls_name = line_lv[160:169].strip()
            lv_launchPad = line_lv[169:193].strip()
            lv_outcome = line_lv[193:194].strip()

            # collecting data from satcat.txt, namely satellite owner and orbitClass
            # using SATCAT to find a matching line
            for x in range(len(sat_array)):
                # SATCAT have an extra 0 digit in satcat.txt, dealing with that
                if sat_array[x][0:8].strip()==("S0"+line_lv[113:120].strip()):
                    match = x

            sat_owner = sat_array[match][89:102].strip()
            sat_orbitClass = sat_array[match][156:165].strip()

            # just for debugging purposes
            sys.stdout.write("processing year: "+lv_launchDate[0:4]+"; entry: "+str(cnt)+"\r")

            # exporting collected data
            with open(output, 'a') as f:
                f.write(lv_launchID.ljust(12) + lv_launchDate.ljust(18) + lv_type.ljust(23) + lv_serial.ljust(20) + lv_prePayload.ljust(30) + lv_postPayload.ljust(30) + sat_owner.ljust(14) + sat_orbitClass.ljust(10) + ls_state.ljust(5) + ls_name.ljust(9) + lv_launchPad.ljust(25) + lv_outcome.ljust(2) + "\n")

        # skipping lines with payload data only
        else: pass

        filler = ""
        f_month = ""
        line_lv = fp.readline()
        cnt += 1

# just for debugging purposes
toc = time.perf_counter()
print(f"\nRuntime: {toc - tic:0.0f} seconds")
