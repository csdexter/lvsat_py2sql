## Description

Script for parsing historical orbital launch data into SQL statements.
Original data source are the following lists https://planet4589.org/space/log/launchlogy.txt and
https://www.planet4589.org/space/log/satcat.txt both created and maintained by Jonathan C. McDowell. Source files used with permission from their author.

## launchlogy.txt format

    000 launchID    text      Launch (international designation)
    013 launchDate  timestamp Launch Date (UTC)
    034 COSPAR      text      COSPAR designation (payload)
    055 postPayload text      Payload name (after launch)
    086 prePayload  text      Payload name (before launch)
    112 SATCAT      text      SATCAT number (payload)
    121 LV_type     text      LV type and name
    144 LV_serial   text      LV serial number
    160 launchSite  text      Launch site (incl. pad)
    193 outcome     text      Outcome
    198 ref         text      Reference

## satcat.txt format

    000  SATCAT     text      SATCAT number
    008  COSPAR     text      COSPAR designation
    023  satName    text      Official name
    064  secName    text      Secondary name or prelaunch name.
    089  owner      text      Owner/Operator
    102  launchDate timestamp Launch Date (UTC)
    114  currStatus text      Current Status
    132  dateStatus timestamp Date of Status
    144  orbitEpoch timestamp Date of orbit epoch
    156  orbitClass text      Orbital class
    165  orbitPrd   text      Orbit period (minutes)
    175  orbitPAI   text      Orbit Perigee x Apogee x Inclination

## Features

 - parsing launchlogy.txt
 - parsing satcat.txt

## TODO

 - choosing more satellite data
 - online mode?
 - easier updating?
 - code cleanup

## Usage

	python lvsat_py2sql.py >> launchesdb.sql

In order for this to work, make sure you have both reference files mentioned above in the same folder as this script. Also, please read the Quirks section below. A generated and fully usable `launchesdb.sql` file is also provided, but you can generate your own updated version. 

The script assumes you have Python3 installed and a suited PostgreSQL database aready created and configured, as specified below:
    
	CREATE DATABASE launchesdb;

	CREATE TABLE launches (
	launchID TEXT,
	launchDate TIMESTAMP,
	COSPAR TEXT,
	postPayload TEXT,
	prePayload TEXT,
	SATCAT TEXT,
	LV_type TEXT,
	LV_serial TEXT,
	launchSite TEXT,
	outcome TEXT
	);
		
	CREATE TABLE satellites (
	launchID TEXT,
	COSPAR TEXT,
	postPayload TEXT,
	prePayload TEXT,
	owner TEXT,
	SATCAT TEXT,
	orbitPrd TEXT,
	orbitClass TEXT,
	orbitPAI TEXT
	);
	
### Quirks

There are two dirty little things that needs to be taken care of outside this script, before the resulting `launchesdb.sql` file could be imported into a database. I was too lazy to have the script do this, maybe I will in the future. Namely, in both `satcat.txt` and `launchlogy.txt` files there's an entry called "Ven{\mu}s" that causes an error during database import. I manually modify that to "Venmus" (this can be done before or after parsing the files: modifying the original files or modifying the resulted `launchesdb.sql` file). Then, PostgreSQL doesn't like entries with apostrophe, so I used a text editor to replace all the apostrophes from both `satcat.txt` and `launchlogy.txt` files, before parsing them with the script.
