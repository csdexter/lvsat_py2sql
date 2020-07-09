## Description

Script for parsing historical orbital launch data into SQL statements.
Original data source are the following lists https://planet4589.org/space/log/launchlogy.txt and
https://www.planet4589.org/space/log/satcat.txt both created and maintained by Jonathan C. McDowell.

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

	python lvsat_py2sql.py >> launches.sql

In order for this to work, make sure you have both reference files mentioned above in the same folder as this script.

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
	COSPAR TEXT,
	postPayload TEXT,
	prePayload TEXT,
	owner TEXT,
	SATCAT TEXT,
	orbitPrd TEXT,
	orbitClass TEXT,
	orbitPAI TEXT
	);

