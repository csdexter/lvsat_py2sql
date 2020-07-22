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
lv_temp = ""

filepath_lv = 'launchlog.txt'
filepath_sat = 'satcat.txt'
filepath_site = 'sites.txt'
output = 'output.txt'
output_sql = 'output.sql'

rw_except_vafb = ["1994-F03","1995-017","1995-017","1995-F03","1996-014","1996-031","1996-037","1996-049","1997-037","1998-012","1998-020","1998-071", "1999-011", "1999-026", "2000-030", "2003-030"]
rw_except_cc = ["1998-060", "2002-004", "2003-004", "2003-017"]

with open(output, 'w') as f:
    f.write("")

with open(output_sql, 'w') as g:
    g.write("")

with open(output_sql, 'w') as g:

    g.write("DROP TABLE launches;\n")

    g.write("CREATE TABLE launches (\n")
    g.write("launchID TEXT,\n")
    g.write("launchDate TIMESTAMP,\n")
    g.write("lv_type TEXT,\n")
    g.write("lv_serial TEXT,\n")
    g.write("lv_Payload TEXT,\n")
    g.write("sat_currStatus TEXT,\n")
    g.write("sat_dateStatus TEXT,\n")
    g.write("sat_orbitClass TEXT,\n")
    g.write("ls_state TEXT,\n")
    g.write("lv_name TEXT,\n")
    g.write("lv_launchPad TEXT,\n")
    g.write("lv_outcome TEXT\n")
    g.write(");\n")

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
            if line_lv[25:27].strip() == "" : lv_launchDate = line_lv[13:18].strip()+f_month+line_lv[22:23].strip()+filler+line_lv[23:27]

            lv_COSPAR = line_lv[40:55].strip()
            lv_postPayload = line_lv[55:86].strip().replace("Ven{\\mu}s", "Venmus")
            lv_prePayload = line_lv[86:112].strip().replace("Ven{\\mu}s", "Venmus")
            if lv_prePayload.strip() == lv_postPayload.strip() or len(lv_prePayload)>16 or len(lv_postPayload)>16:
                lv_Payload = lv_postPayload
            else:
                lv_Payload = lv_postPayload.strip() + " (" + lv_prePayload.strip() + ")"
            lv_SATCAT = line_lv[112:121].strip()
            lv_type = line_lv[121:144].strip()

            # adjusting the names of some rockets
            if lv_type == "Soyuz-2-1A": lv_type = "Soyuz-2.1a"
            if lv_type == "Soyuz-2-1B": lv_type = "Soyuz-2.1b"
            if lv_type == "Soyuz-2-1V": lv_type = "Soyuz-2.1v"
            if lv_type == "Falcon 9"  : lv_type = "Falcon-9"
            if "Chang Zheng" in lv_type: lv_type = lv_type.replace("Chang Zheng ","CZ-")

            lv_serial = line_lv[144:160].strip()
            if lv_serial == "-": lv_serial = ""

            lv_name = line_lv[160:169].strip()
            # since orbital launches locations are just a small subset of sites.text
            # why not displaying them in a much more familiar name?
            if lv_name == "NIIP-5":
                lv_name = "Baikonur"
                if int(lv_launchDate[0:4])>1991:
                    ls_state = "RU"
                else:
                    ls_state = "SU"
            if lv_name == "GIK-5":
                lv_name = "Baikonur"
                if int(lv_launchDate[0:4])>1991:
                    ls_state = "RU"
                else:
                    ls_state = "SU"
            if lv_name == "NIIP-53":
                lv_name = "Plesetsk"
                if int(lv_launchDate[0:4])>1991:
                    ls_state = "RU"
                else:
                    ls_state = "SU"
            if lv_name == "GIK-1":
                lv_name = "Plesetsk"
                if int(lv_launchDate[0:4])>1991:
                    ls_state = "RU"
                else:
                    ls_state = "SU"
            if lv_name == "GNIIPV":
                lv_name = "Plesetsk"
                if int(lv_launchDate[0:4])>1991:
                    ls_state = "RU"
                else:
                    ls_state = "SU"
            if lv_name == "V":
                lv_name = "VAFB"
                ls_state = "US"
            if lv_name == "VS":
                lv_name = "SVAFB"
                ls_state = "US"
            if lv_name == "MAHIA":
                lv_name = "Mahia"
                ls_state = "US"
            if lv_name == "WI" or lv_name == "WIMB":
                lv_name = "Wallops"
                ls_state = "US"
            if lv_name == "GTsP-4" or lv_name == "GTsMP-4":
                lv_name = "Kapustin"
                ls_state = "SU"
            if lv_name == "KASC":
                lv_name = "Kagoshima"
                ls_state = "JP"
            if lv_name == "WOO":
                lv_name = "Woomera"
                ls_state = "AU"
            if lv_name == "CSG":
                lv_name = "Kourou"
                ls_state = "EU"
            if lv_name == "JQ":
                lv_name = "Jiuquan"
                ls_state = "CN"
            if lv_name == "XSC":
                lv_name = "Xichang"
                ls_state = "CN"
            if lv_name == "TNSC":
                lv_name = "Tanegashima"
                ls_state = "JP"
            if lv_name == "PALB":
                lv_name = "Palmachim"
                ls_state = "IL"
            if lv_name == "CC":
                ls_state = "US"
            if lv_name == "WEN":
                lv_name = "Wenchang"
                ls_state = "CN"
            if lv_name == "TYSC":
                lv_name = "Taiyuan"
                lv_state = "CN"
            if lv_name == "MARS":
                lv_name = "Wallops"
                lv_state = "US"
            if lv_name == "VOST":
                lv_name = "Vostochny"
                lv_state = "RU"

            lv_launchPad = line_lv[169:193].strip()
            lv_outcome = line_lv[193:194].strip()

            # collecting data from satcat.txt, namely satellite owner and orbitClass
            # using SATCAT to find a matching line
            for x in range(len(sat_array)):
                # SATCAT have an extra 0 digit in satcat.txt, dealing with that
                if sat_array[x][0:8].strip()==("S0"+line_lv[113:120].strip()):
                    match = x

            # sat_owner is flawed, since it's not mentioned for failed launches; do not use this
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
            if sat_currStatus == "Landed" or sat_currStatus == "Landed Att": sat_currStatus = "LAN"
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
                if (g_month == "") :
                    sat_dateStatus = ""
                else:
                    sat_dateStatus = sat_array[match][131:135].strip()+g_month+date_partial

            # just for debugging purposes
            sys.stdout.write("processing year: "+lv_launchDate[0:4]+"; entry: "+str(cnt)+"\r")

            # if malformed dates are still present, just ignore them
            if len(sat_dateStatus) < 10: sat_dateStatus = ""

            # if there is no new post launch sat name, use pre launch sat name
            if len(lv_postPayload.strip()) < 3:
                lv_postPayload = lv_prePayload.strip()

            # dealing with Starlink launches and their names
            if lv_launchID == "2019-029": lv_postPayload = lv_prePayload = "[Starlink-0]"
            if lv_launchID == "2019-074": lv_postPayload = lv_prePayload = "[Starlink-1]"
            if lv_launchID == "2020-001": lv_postPayload = lv_prePayload = "[Starlink-2]"
            if lv_launchID == "2020-006": lv_postPayload = lv_prePayload = "[Starlink-3]"
            if lv_launchID == "2020-012": lv_postPayload = lv_prePayload = "[Starlink-4]"
            if lv_launchID == "2020-019": lv_postPayload = lv_prePayload = "[Starlink-5]"
            if lv_launchID == "2020-025": lv_postPayload = lv_prePayload = "[Starlink-6]"
            if lv_launchID == "2020-035": lv_postPayload = lv_prePayload = "[Starlink-7]"
#            if lv_launchID = "XXX": lv_postPayload = lv_prePayload = "[Starlink-8]"
#            if lv_launchID = "XXX": lv_postPayload = lv_prePayload = "[Starlink-9]"

            # fixing the pads and locations for rockets launched from airplanes
            lv_temp = lv_name+lv_launchPad
            if lv_temp.find("RW") > 1:
                lv_temp = lv_name+lv_launchPad
                lv_launchPad = lv_temp.partition(",")[0]
                lv_name = lv_temp[lv_temp.find(",")+1:lv_temp.find(" ")]

            # argh, screw it, I'm going to just hardcode this, I hope no one is reading this
            if lv_launchID in rw_except_vafb: lv_name = "VAFB"
            if lv_launchID in rw_except_cc: lv_name = "CC"

            # failed launches does not have sat_orbitClass and sat_dateStatus and sat_currStatus
            if lv_SATCAT[0]=="F": sat_currStatus = sat_dateStatus = sat_orbitClass = ""

            # exporting collected data
            with open(output, 'a') as f:
                f.write(lv_launchID.ljust(11) + lv_launchDate.ljust(18) + lv_type.ljust(23) + lv_serial.ljust(20) + lv_Payload.ljust(45) + sat_currStatus.ljust(5) + sat_dateStatus.ljust(12) + sat_orbitClass.ljust(10) + ls_state.ljust(5) + lv_name.ljust(12) + lv_launchPad.ljust(10) + lv_outcome.ljust(2) + "\n")
            with open(output_sql, 'a') as g:
                g.write("INSERT INTO launches VALUES ('"+ lv_launchID +"','"+ lv_launchDate +"','"+ lv_type.replace("'","''") +"','"+ lv_serial +"','"+ lv_Payload.replace("'","''") + "','"+ sat_currStatus +"','"+ sat_dateStatus +"','"+ sat_orbitClass +"','"+ ls_state +"','"+ lv_name +"','"+ lv_launchPad +"','"+ lv_outcome + "');" + "\n")
        # skipping lines with payload data only
        else: pass

        filler = ""
        f_month = ""
        line_lv = fp.readline()
        cnt += 1

# just for debugging purposes
toc = time.perf_counter()
print(f"\nRuntime: {toc - tic:0.0f} seconds")
