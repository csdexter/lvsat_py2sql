## Description

Script for parsing historical orbital launch data into SQL statements.

Original data source are the following lists (not redistributed here, get them from their original location to ensure you have the latest version), created and maintained by Jonathan C. McDowell and used here with permission from their author.

- Standard master orbital list (https://planet4589.org/space/log/launchlogy.txt)
- Master Satellite List (https://www.planet4589.org/space/log/satcat.txt)
- Launch Sites Database (https://planet4589.org/space/gcat/data/tables/sites.html)

## launchlogy.txt format

    000 launchID    text      Launch (international designation)
    013 launchDate  timestamp Launch Date (UTC)
    034 COSPAR      text      COSPAR designation (payload)
    055 postPayload text      Payload name (after launch)
    086 prePayload  text      Payload name (before launch)
    112 SATCAT      text      SATCAT number (payload)
    121 LV_type     text      LV type and name
    144 LV_serial   text      LV serial number
    160 launchSite  text      Launch site
    169 launchPad   text      Launch pad
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

## sites.txt format

    000 lsSite      text      Launch site code (as in launchlogy.txt)
    040 lsState     text      Launch site state (country)
    093 lsName      text      Launch site full name

## Features

 - parsing launchlogy.txt
 - parsing satcat.txt
 - parsing sites.txt (for country and launchpad sites data)
 - cleaning up the strings for PostgreSQL compliant format

## TODO

 - choosing more satellite data
 - integrating launch sites/complexes
 - online mode?
 - easier updating?
 - code cleanup and optimization

## Usage

	python lvsat_py2sql.py >> launchesdb.sql

In order for this to work, make sure you have both reference files mentioned above in the same folder as this script. A generated and fully usable `launchesdb.sql` file is also provided, but you can generate your own updated version.

The generated database contains two tables, one for launch attempts and another one for satellites.

The script assumes you have Python3 installed and a suited PostgreSQL database already created and configured, as specified below:

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
