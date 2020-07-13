## Description

Script for parsing historical orbital launch data into SQL statements.

Original data source are the following lists (not redistributed here, get them from their original location to ensure you have the latest version), created and maintained by Jonathan C. McDowell and used here with permission from their author.

- Standard master orbital list (https://planet4589.org/space/log/launchlogy.txt)
- Full master orbital list (https://planet4589.org/space/log/launchlog.txt)
- Master Satellite List (https://www.planet4589.org/space/log/satcat.txt)
- Launch Sites Database (https://planet4589.org/space/gcat/data/tables/sites.html)
- Organizations Database (https://planet4589.org/space/gcat/data/tables/orgs.html)

## launchlog.txt format

    000 lv_launchID      TEXT      Launch (international designation)
    013 lv_launchDate    TIMESTAMP Launch Date (UTC)
    034 lv_COSPAR        TEXT      COSPAR designation (payload)
    055 lv_postPayload   TEXT      Payload name (after launch)
    086 lv_prePayload    TEXT      Payload name (before launch)
    112 lv_SATCAT        TEXT      SATCAT number (payload)
    121 lv_type          TEXT      LV type and name
    144 lv_serial        TEXT      LV serial number
    160 lv_launchSite    TEXT      Launch site
    169 lv_launchPad     TEXT      Launch pad
    193 lv_outcome       TEXT      Outcome
    198 lv_ref           TEXT      Reference

## satcat.txt format

    000 sat_SATCAT       TEXT      SATCAT number
    008 sat_COSPAR       TEXT      COSPAR designation
    023 sat_postPayload  TEXT      Official name
    064 sat_prePayload   TEXT      Secondary name or prelaunch name.
    089 sat_owner        TEXT      Owner/Operator
    102 sat_launchDate   TIMESTAMP Launch Date (UTC)
    114 sat_currStatus   TEXT      Current Status
    132 sat_dateStatus   TIMESTAMP Date of Status
    144 sat_orbitEpoch   TIMESTAMP Date of orbit epoch
    156 sat_orbitClass   TEXT      Orbital class
    165 sat_orbitPrd     TEXT      Orbit period (minutes)
    175 sat_orbitPAI     TEXT      Orbit Perigee x Apogee x Inclination

## sites.txt format

    000 ls_site          TEXT      Launch site code (as in launchlogy.txt)
    040 ls_state         TEXT      Launch site state (country)
    093 ls_name          TEXT      Launch site full name

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
    lv_launchID TEXT,
    lv_launchDate TIMESTAMP,
    lv_COSPAR TEXT,
    lv_postPayload TEXT,
    lv_prePayload TEXT,
    lv_SATCAT TEXT,
    lv_type TEXT,
    lv_serial TEXT,
    ls_name TEXT,
    lv_launchPad, TEXT,
    ls_state, TEXT,
    lv_outcome TEXT
    );

    CREATE TABLE satellites (
    sat_launchID TEXT,
    sat_COSPAR TEXT,
    sat_postPayload TEXT,
    sat_prePayload TEXT,
    sat_owner TEXT,
    sat_SATCAT TEXT,
    sat_orbitPrd TEXT,
    sat_orbitClass TEXT,
    sat_orbitPAI TEXT
    );
