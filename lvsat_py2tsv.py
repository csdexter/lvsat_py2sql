# experimental, do not touch

import sys
import os
import time

# just for debugging purposes
tic = time.perf_counter()


filler  = ""
filler2 = ""
f_month = ""
g_month = ""
date_partial = ""
ls_state = ""
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
                if ls_state == "GUF": ls_state = "GF"

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
            lv_name = line_lv[160:169].strip()
            if lv_name == "NIIP-5": lv_name = "Baikonur"
            if lv_name == "NIIP-53": lv_name = "Plesetsk"
            if lv_name == "V": lv_name = "VAFB"

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
            sat_currStatus = sat_array[match][114:131].strip()

            # Treating each case independently, to code them and thus clear the table a bit
            if sat_currStatus == "Reentered": sat_currStatus = "REE"
            if sat_currStatus == "Reentered Att": sat_currStatus = "REA"
            if sat_currStatus == "In Earth orbit": sat_currStatus = "IEO"
            if sat_currStatus == "Deep Space": sat_currStatus = "DSO"
            if sat_currStatus == "Beyond Earth orb": sat_currStatus = "BEO"
            if sat_currStatus == "Lost": sat_currStatus = "LST"
            if sat_currStatus == "Landed": sat_currStatus = "LAN"
            if sat_currStatus == "Deorbited": sat_currStatus = "DOR"
            if sat_currStatus == "Deep Space Att": sat_currStatus = "DSA"
            if sat_currStatus == "Exploded": sat_currStatus = "EXP"

            # converting date for sat_dateStatus variable to a format compliant with PostgreSQL
            if len(sat_array[match]) < 140 : sat_dateStatus = ""
            else:
                date_partial = sat_array[match][140:142]
                if sat_array[match][140].strip()=='' :
                    date_partial = "0"+sat_array[match][141]
                g_month = ""
                if sat_array[match][131:141].strip() != "" :
                    if sat_array[match][149:152] == "Jan" : g_month="-01-"
                    if sat_array[match][149:152] == "Feb" : g_month="-02-"
                    if sat_array[match][149:152] == "Mar" : g_month="-03-"
                    if sat_array[match][149:152] == "Apr" : g_month="-04-"
                    if sat_array[match][149:152] == "May" : g_month="-05-"
                    if sat_array[match][149:152] == "Jun" : g_month="-06-"
                    if sat_array[match][149:152] == "Jul" : g_month="-07-"
                    if sat_array[match][149:152] == "Aug" : g_month="-08-"
                    if sat_array[match][149:152] == "Sep" : g_month="-09-"
                    if sat_array[match][149:152] == "Oct" : g_month="-10-"
                    if sat_array[match][149:152] == "Nov" : g_month="-11-"
                    if sat_array[match][149:152] == "Dec" : g_month="-12-"
                if g_month == "" :
                    sat_dateStatus = ""
                else:
                    sat_dateStatus = sat_array[match][131:135].strip()+g_month+date_partial

            # just for debugging purposes
            sys.stdout.write("processing year: "+lv_launchDate[0:4]+"; entry: "+str(cnt)+"\r")

            # exporting collected data
            with open(output, 'a') as f:
                f.write(lv_launchID.ljust(12) + lv_launchDate.ljust(18) + lv_type.ljust(23) + lv_serial.ljust(20) + sat_owner.ljust(14) + lv_prePayload.ljust(30) + lv_postPayload.ljust(30)+ sat_currStatus.ljust(5) + sat_dateStatus.ljust(12) + sat_orbitClass.ljust(10) + ls_state.ljust(5) + lv_name.ljust(10) + lv_launchPad.ljust(25) + lv_outcome.ljust(2) + "\n")

        # skipping lines with payload data only
        else: pass

        filler = ""
        f_month = ""
        line_lv = fp.readline()
        cnt += 1

# just for debugging purposes
toc = time.perf_counter()
print(f"\nRuntime: {toc - tic:0.0f} seconds")
