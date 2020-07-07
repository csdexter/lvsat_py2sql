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
