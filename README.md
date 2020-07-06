## Description

Script for parsing historical orbital launch data into SQL statements
Original data source are the following lists https://planet4589.org/space/log/launchlogy.txt and
https://www.planet4589.org/space/log/satcat.txt both maintained by Jonathan C. McDowell.

## launchlogy.txt format

000 Launch (international designation)
013 Launch Date (UTC)
034 COSPAR designation (payload)
055 Payload name (after launch)
086 Payload name (before launch)
112 SATCAT number (payload)
121 LV type and name
144 LV serial number
160 Launch site (incl. pad)
193 Outcome
198 Reference

## satcat.txt format

000 SATCAT number
008 COSPAR designation
023 Official name
064 Secondary name or prelaunch name.
089 Owner/Operator
102 Launch Date (UTC)
114 Current Status
132 Date of Status
144 Date of orbit epoch
156 Orbit class
165 Orbit period, minutes
175 Perigee x Apogee x Inclination

## Features

- Parsing launchlogy.txt

## TODO 
 - parsing satcat.txt
 - online mode
 - easier updating?
 
## USAGE 

In order for this to work, make sure you have both reference files mentioned above in the same folder as this script.

The script assumes you have a suited database aready created (more details to follow)

    python lvsat_py2sql.py >> launches.sql

