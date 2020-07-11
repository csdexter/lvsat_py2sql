## Description

Script for parsing historical orbital launch data into SQL statements.

Original data source are the following lists (not redistributed here, get them from their original location to ensure you have the latest version), created and maintained by Jonathan C. McDowell and used here with permission from their author.

- Standard master orbital list (https://planet4589.org/space/log/launchlogy.txt)
- Master Satellite List (https://www.planet4589.org/space/log/satcat.txt)
- Launch Sites Database (https://planet4589.org/space/gcat/data/tables/sites.html)

## launchlogy.txt format

    000 launchID    TEXT      Launch (international designation)
    013 launchDate  TIMESTAMP Launch Date (UTC)
    034 COSPAR      TEXT      COSPAR designation (payload)
    055 postPayload TEXT      Payload name (after launch)
    086 prePayload  TEXT      Payload name (before launch)
    112 SATCAT      TEXT      SATCAT number (payload)
    121 LV_type     TEXT      LV type and name
    144 LV_serial   TEXT      LV serial number
    160 launchSite  TEXT      Launch site
    169 launchPad   TEXT      Launch pad
    193 outcome     TEXT      Outcome
    198 ref         TEXT      Reference

## satcat.txt format

    000  SATCAT     TEXT      SATCAT number
    008  COSPAR     TEXT      COSPAR designation
    023  satName    TEXT      Official name
    064  secName    TEXT      Secondary name or prelaunch name.
    089  owner      TEXT      Owner/Operator
    102  launchDate TIMESTAMP Launch Date (UTC)
    114  currStatus TEXT      Current Status
    132  dateStatus TIMESTAMP Date of Status
    144  orbitEpoch TIMESTAMP Date of orbit epoch
    156  orbitClass TEXT      Orbital class
    165  orbitPrd   TEXT      Orbit period (minutes)
    175  orbitPAI   TEXT      Orbit Perigee x Apogee x Inclination

## sites.txt format

    000 lsSite      TEXT      Launch site code (as in launchlogy.txt)
    040 lsState     TEXT      Launch site state (country)
    093 lsName      TEXT      Launch site full name

## Features

 - parsing launchlogy.txt
 - parsing satcat.txt
 - parsing sites.txt (for country and launchpad sites data)
 - cleaning up the strings for PostgreSQL compliant format

## TODO

 - more satellite data
 - online mode?
 - some updating mechanism?
 - code clean-up and optimization

## Usage

	python lvsat_py2sql.py >> launchesdb.sql

In order for this to work, make sure you have both reference files mentioned above in the same folder as this script.

The script assumes you have Python3 installed and a suited PostgreSQL database already created and configured, as specified below. If not, the script can create the database structure for you, by running:

	python lvsat_py2sql.py --reinit >> launchesdb.sql

This is useful (and encouraged) for updating from more recent source files.

*WARNING*: running the script with `--reinit` switch will create a file that, when imported into PostgreSQL, will drop your database and tables related to this script, before creating a new database structure and populating it with new data. Make sure you backup your data first, if needed.

Final step: simply import the created `launchesdb.sql` in PostgreSQL.

### Database structure  

The generated database contains two tables, one for launch attempts and another one for satellites, as seen below:

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
    launchPad, TEXT,
    lsState, TEXT,
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
