#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Import historical orbital launch data into an SQL database.

   Copyright (C) 2020 Claudiu Tănăselia <your email here>.

   Released under the <your licence here>.
"""
import argparse
import calendar
import csv
from datetime import datetime, date
import locale
import logging
import os
import sys
import time

import requests
from six import iteritems

__author__ = 'Claudiu Tănăselia <your email here>'

_FLAGS = argparse.ArgumentParser(
    description='Converts orbital launch data to SQL',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
# Python's argparse is light years behind absl.flags so we need to hand-hold it
# for booleans :-(
_FLAGS_DOWNLOAD = _FLAGS.add_mutually_exclusive_group(required=False)
_FLAGS_DOWNLOAD.add_argument(
    '--download', dest='download',
    help='Automatically download needed input data from '
    'https://www.planet4589.org/ if not found in --datadir.',
    action='store_true')
_FLAGS_DOWNLOAD.add_argument(
    '--no-download', dest='download',
    help='Reverse of --download, fail if any input file is missing.',
    action='store_false')
_FLAGS.set_defaults(download=True)
_FLAGS_UPDATE = _FLAGS.add_mutually_exclusive_group(required=False)
_FLAGS_UPDATE.add_argument(
    '--update', dest='update',
    help='If --download was given and an input file is present but older than '
    'the version on https://www.planet4589.org/, download the newer version '
    'and overwrite the local copy.',
    action='store_true')
_FLAGS_UPDATE.add_argument(
    '--no-update', dest='update',
    help='Reverse of --update, do not attempt to check for freshness (and '
    'download) any input file that is already present.',
    action='store_false')
_FLAGS.set_defaults(update=False)
_FLAGS.add_argument(
    '-D', '--datadir', default=os.getcwd(),
    help='Directory from which to read input data files (--orbitalist, '
    '--satellitelist, --siteslist).')
_FLAGS.add_argument(
    '-R', '--orbitalist', default='launchlogy.txt',
    help='Name of file inside --datadir containing the standard master orbital '
    'list.')
_FLAGS.add_argument(
    '-L', '--satellitelist', default='satcat.txt',
    help='Name of file inside --datadir containing the master satellite list.')
_FLAGS.add_argument(
    '-S', '--sitelist', default='sites.tsv',
    help='Name of file inside --datadir containing the launch sites list (in '
    'TSV format).')
_FLAGS.add_argument(
    '-O', '--output', default=os.path.join(os.getcwd(), 'lvsat.sql'),
    help='File name to store SQL output into, will be overwritten if already '
    'existing. Use "-" to specify stdout.')
_FLAGS.add_argument(
    '--add-drop', dest='adddrop', default=False,
    help='Prepend DROP/CREATE TABLE statements to the output.',
    action='store_true')
_LOG = logging.getLogger(__name__)

_FILE_ORBITAL = 1
_FILE_SATELLITE = 2
_FILE_SITE = 3
_INPUT_SOURCES = {
    _FILE_ORBITAL: 'https://www.planet4589.org/space/log/launchlogy.txt',
    _FILE_SATELLITE: 'https://www.planet4589.org/space/log/satcat.txt',
    _FILE_SITE: 'https://www.planet4589.org/space/gcat/tsv/tables/sites.tsv'}
_DSIT2ISO = {
    'A': 'AT',
    'B': 'BE',
    'C': 'CU',
    'D': 'DE',
    'E': 'ES',
    'F': 'FR',
    'G': 'GA',
    'H': 'HU',
    'I': 'IT',
    'J': 'JP',
    'K': 'KH',
    'L': 'LU',
    'M': 'MT',
    'N': 'NO',
    'P': 'PT',
    'Q': 'QA',
    'S': 'SE',
    'T': 'TH',
    'V': 'VA',
    'Z': 'ZM'}


def add_drop(output):
    """Adds DROP/CREATE statements in SQL output.

    Args:
      output: (file)-like object that the output will be written to.
    """
    output.write(
        """DROP TABLE IF EXISTS data_Satellite;
DROP TABLE IF EXISTS data_Launch;
DROP TABLE IF EXISTS index_SatelliteOwner;
DROP TABLE IF EXISTS index_SatelliteStatus;
DROP TABLE IF EXISTS index_SatelliteOrbitClass;
DROP TABLE IF EXISTS index_LaunchVehicleType;
DROP TABLE IF EXISTS index_Site;
DROP TABLE IF EXISTS index_SiteType;
DROP TABLE IF EXISTS index_SiteCountry;
DROP TABLE IF EXISTS index_SiteOperator;

CREATE TABLE index_SiteType (
  id bigint(20) unsigned NOT NULL PRIMARY KEY,
  siteType char(2) NOT NULL
);

CREATE TABLE index_SiteCountry (
  id bigint(20) unsigned NOT NULL PRIMARY KEY,
  siteCountryCode varchar(8) NOT NULL
);

CREATE TABLE index_SiteOperator (
  id bigint(20) unsigned NOT NULL PRIMARY KEY,
  siteOperatorCode varchar(16) NOT NULL
);

CREATE TABLE index_LaunchVehicleType (
  id bigint(20) unsigned NOT NULL PRIMARY KEY,
  launchVehicleType varchar(24) NOT NULL
);

CREATE TABLE index_Site (
  id varchar(8) NOT NULL PRIMARY KEY,
  typeID bigint(20) unsigned NOT NULL,
  countryID bigint(20) unsigned NOT NULL,
  dateStart date DEFAULT NULL,
  dateEnd date DEFAULT NULL,
  shortName varchar(16) NOT NULL,
  fullName varchar(128) NOT NULL,
  locationName varchar(64) NOT NULL,
  locationLat float DEFAULT NULL,
  locationLon float DEFAULT NULL,
  locationError float NOT NULL,
  operatorID bigint(20) unsigned NOT NULL,
  FOREIGN KEY (typeID) REFERENCES index_SiteType(id),
  FOREIGN KEY (countryID) REFERENCES index_SiteCountry(id),
  FOREIGN KEY (operatorID) REFERENCES index_SiteOperator(id)
);

CREATE TABLE data_Launch (
  id varchar(16) NOT NULL PRIMARY KEY,
  datetime datetime NOT NULL,
  launchVehicleTypeID bigint(20) unsigned NOT NULL,
  launchVehicleSerial varchar(16) NOT NULL,
  siteID varchar(8) NOT NULL,
  launchPad varchar(24) NOT NULL,
  outcome tinyint(1) NOT NULL,
  reference varchar(24) NOT NULL,
  FOREIGN KEY (launchVehicleTypeID) REFERENCES index_LaunchVehicleType(id),
  FOREIGN KEY (siteID) REFERENCES index_Site(id)
);

CREATE TABLE index_SatelliteOwner (
  id bigint(20) unsigned NOT NULL PRIMARY KEY,
  satelliteOwnerCode varchar(16) NOT NULL
);

CREATE TABLE index_SatelliteStatus (
  id bigint(20) unsigned NOT NULL PRIMARY KEY,
  satelliteStatus varchar(24) NOT NULL
);

CREATE TABLE index_SatelliteOrbitClass (
  id bigint(20) unsigned NOT NULL PRIMARY KEY,
  satelliteOrbitClass varchar(8) NOT NULL
);

CREATE TABLE data_Satellite (
  id char(8) NOT NULL PRIMARY KEY,
  launchID varchar(16) NOT NULL,
  cospar varchar(16) NOT NULL,
  initialName varchar(48) NOT NULL,
  finalName varchar(32) NOT NULL,
  ownerID bigint(20) unsigned NOT NULL,
  statusID bigint(20) unsigned NOT NULL,
  statusDate date DEFAULT NULL,
  orbitEpoch date DEFAULT NULL,
  orbitClassID bigint(20) unsigned NOT NULL,
  orbitPeriod float DEFAULT NULL,
  orbitPerigee float DEFAULT NULL,
  orbitApogee float DEFAULT NULL,
  orbitInclination float DEFAULT NULL,
  FOREIGN KEY (launchID) REFERENCES data_Launch(id),
  FOREIGN KEY (ownerID) REFERENCES index_SatelliteOwner(id),
  FOREIGN KEY (statusID) REFERENCES index_SatelliteStatus(id),
  FOREIGN KEY (orbitClassID) REFERENCES index_SatelliteOrbitClass(id)
);
""")


def retrieve_file(from_url, to_file, if_older_than=None):
    """Retrieves one input file via HTTP.

    Args:
      from_url: (str) URL to retrieve the input file from
      to_file: (str) fully qualified path name to store the file as
      if_older_than: (float) UNIX timestamp or None. If given, only retrieve a
                     new copy if it's newer than the given timestamp.
    """
    the_headers = None
    if if_older_than is not None:
        # gmtime() will read a UNIX timestamp and output a struct_time with the
        # time zone field set to GMT. strftime() will then correctly output a
        # time zone name of 'GMT'.
        the_headers = {
            'If-Modified-Since': time.strftime(
                '%a, %d %b %Y %H:%M:%S %Z', time.gmtime(if_older_than))}
    request = requests.get(from_url, headers=the_headers)
    if request.status_code == 304:
        _LOG.info('Input file "%s" still fresh, no action taken.', to_file)
        return
    elif request.status_code == 200:
        if if_older_than is None:
            _LOG.info('Input file "%s" downloaded successfully.', to_file)
        else:
            _LOG.warning('Input file "%s" updated successfully.', to_file)
    else:
        if if_older_than is None:
            _LOG.fatal(
                'Unable to download input file "%s", cannot continue! '
                '(HTTP: %d)', to_file, request.status_code)
        else:
            _LOG.warning(
                'Unable to update input file "%s", continuing with stale data! '
                '(HTTP: %d)', to_file, request.status_code)
            return
    with open(to_file, 'wb') as the_file:
        the_file.write(request.content)
    # HTTP dates are by definition in GMT, strptime() will parse a time zone
    # name but doesn't adjust the actual fields to match. timegm() will do
    # that for us and then utime() will result in the correct MTime getting
    # applied to the retrieved file.
    mtime = calendar.timegm(time.strptime(request.headers['Last-Modified'],
                                          '%a, %d %b %Y %H:%M:%S %Z'))
    os.utime(to_file, (mtime, mtime))


def ensure_present(input_name, input_url, fetch_input, update_input):
    """Ensures a given input file is present and readable.

    Args:
      input_name: (str) fully qualified path name of input file to check
      input_url: (str) the URL to fetch/update the input file from
      fetch_input: (bool) whether to fetch the input file from input_url if
                   missing
      update_input: (bool) whether to fetch the input file from input_url if
                    present but older than the URL.
    """
    if os.path.isdir(input_name):
        _LOG.fatal(
            'Input file "%s" appears to be a directory, cannot continue!',
            input_name)
    if not os.path.exists(input_name):
        if not fetch_input:
            _LOG.fatal(
                'Input file "%s" does not exist and --download was not given, '
                'cannot continue!', input_name)
        else:
            if not os.path.isdir(os.path.dirname(input_name)):
                _LOG.fatal(
                    'Directory "%s" for missing input file "%s" does not '
                    'exist, cannot download there!',
                    os.path.dirname(input_name), input_name)
            if not os.access(os.path.dirname(input_name), os.W_OK):
                _LOG.fatal(
                    'Directory "%s" for missing input file "%s" is not '
                    'writable, cannot download there!',
                    os.path.dirname(input_name), input_name)
            _LOG.warning(
                'Input file "%s" missing, downloading from "%s"!',
                input_name, input_url)
            retrieve_file(input_url, input_name)
    else:
        if not os.access(input_name, os.R_OK):
            _LOG.fatal(
                'Input file "%s" exists but is not readable, cannot continue! ',
                input_name)
        else:
            if update_input:
                retrieve_file(
                    input_url, input_name, os.stat(input_name).st_mtime)
    _LOG.info('Input file "%s" (now) present and readable.', input_name)


def parse_date(text_date, start_date):
    """Parses dates into Pyton objects.

    Args:
      text_date: (str) date coordinate as present in input
      start_date: (bool) True if this is supposed to be a start date, False if
                  an end date. Used by the reconstruction heuristic when
                  incomplete date data was present in the input.
    Returns:
      (date) representation of input or None
    """
    # Some tables use a blank to denote unknown
    if not text_date:
        return None
    # We coerce both '-' and '?' (unknown) and '*' (still in operation) to None
    if text_date in ('-', '*', '?'):
        return None
    # Some records end with various garbage, because screw machine-readable!
    text_date = text_date.rstrip('?:-')
    # Some records have only year or month precision
    date_fields = len(text_date.split(' '))
    if date_fields == 1:
        # Some records only have decade precision
        if text_date.endswith('s'):
            if start_date:
                text_date = text_date.rstrip('s')
            else:
                text_date = text_date[:-2] + '9'
        # Missing month and day
        if start_date:
            text_date = text_date + ' Jan 1'
        else:
            text_date = text_date + ' Dec 31'
    elif date_fields == 2:
        # Missing day, unless they tried real hard to screw us up with quarters
        if text_date[-2] == 'Q':
            quarter = int(text_date[-1])
            text_date = text_date[:-2]
            if start_date:
                text_date = text_date + {
                    1: 'Jan', 2: 'Apr', 3: 'Jul', 4: 'Oct'}[quarter]
            else:
                text_date = text_date + {
                    1: 'Mar', 2: 'Jun', 3: 'Set', 4: 'Dec'}[quarter]
        if start_date:
            text_date = text_date + ' 1'
        else:
            # TODO(rmihailescu): replace this cheat with proper month size
            text_date = text_date + ' 28'
    return datetime.strptime(text_date, '%Y %b %d').date()


def parse_float(text_float):
    """Parses float data into Python value."""
    try:
        return float(text_float)
    except ValueError:
        return None


def load_satellites(input_name):
    """Loads satellite data.

    Args:
      input_name: (str) fully qualified path name of corresponding input file.
    Returns:
      (tuple) of satellite owner index, satellite status index, satellite orbit
      class and actual satellite data.
    """
    satellites = {}
    owners = set([])
    statuses = set([])
    classes = set([])
    # We need to parse English month names in the input, so we make sure the
    # relevant system libraries will expect English input as well.
    old_locale = locale.setlocale(locale.LC_TIME, 'C')
    # The satellite list has fixed-with fields, the 1970s called and said they
    # want their punch cards back :-(
    with open(input_name, 'rt') as input_file:
        for input_line in input_file:
            owners.add(input_line[89:102].strip())
            statuses.add(input_line[114:131].strip())
            classes.add(input_line[156:165].strip())
            satellites[input_line[0:8].strip()] = {
                'launchID': None,
                'cospar': input_line[8:23].strip(),
                'initialName': input_line[23:64].strip(),
                'finalName': input_line[64:89].strip(),
                'ownerID': input_line[89:102].strip(),
                'statusID': input_line[114:131].strip(),
                'statusDate': parse_date(input_line[131:144].strip(), True),
                'orbitEpoch': parse_date(input_line[144:156].strip(), True),
                'orbitClassID': input_line[156:165].strip(),
                'orbitPeriod': parse_float(input_line[165:174].strip()),
                'orbitPerigee': parse_float(input_line[174:181].strip()),
                'orbitApogee': parse_float(input_line[183:190].strip()),
                'orbitInclination': parse_float(input_line[192:198].strip())}
    _LOG.info('Loaded satellite data.')
    locale.setlocale(locale.LC_TIME, old_locale)
    return (owners, statuses, classes, satellites)


def transform_country_code(old_code):
    """Normalizes country codes in input."""
    # The site data uses a mish-mash of DSIT, ISO3166-1 and invented country
    # codes. We try to coerce the data to sanity by first converting the
    # 1-letter DSIT codes to their 2-letter ISO3166-1 equivalents ...
    new_code = _DSIT2ISO.get(old_code) or old_code
    # ... and then we correct a few known exceptions.
    if new_code == 'GUF':
        new_code = 'GF'
    return new_code


def load_sites(input_name):
    """Loads launch site data.

    Args:
      input_name: (str) fully qualified path name of corresponding input file.
    Returns:
      (tuple) of launch site type index, launch site location country index,
      launch site operator index and actual launch site data.
    """
    sites = {}
    types = set([])
    countries = set([])
    operators = set([])
    # We need to parse English month names in the input, so we make sure the
    # relevant system libraries will expect English input as well.
    old_locale = locale.setlocale(locale.LC_TIME, 'C')
    # The site list has TAB-separated fields, the 1990s called and said they
    # want their amber-on-black CRTs back :-( Still way better than fixed-with!
    with open(input_name, newline='') as input_file:
        tsv_data = csv.reader(input_file, delimiter='\t')
        for input_record in tsv_data:
            if input_record[0] == '#Site':
                # Skip over header line, if present
                continue
            types.add(input_record[3])
            country = transform_country_code(input_record[4])
            countries.add(country)
            operators.add(input_record[13])
            sites[input_record[0]] = {
                'typeID': input_record[3],
                'countryID': country,
                'dateStart': parse_date(input_record[5], True),
                'dateEnd': parse_date(input_record[6], False),
                'shortName': input_record[7],
                'fullName': input_record[8],
                'locationName': input_record[9],
                'locationLat': parse_float(input_record[10]),
                'locationLon': parse_float(input_record[11]),
                'locationError': float(input_record[12]),
                'operatorID': input_record[13]}
    locale.setlocale(locale.LC_TIME, old_locale)
    _LOG.info('Loaded launch site data.')
    return (types, countries, operators, sites)


def prepend_extra_zero(satcat):
    """Fixes a foreign key discrepancy between launch and satellite data."""
    return satcat[0] + '0' + satcat[1:]


def parse_datetime(text_date):
    """Parses date/times into Pyton objects.

    Args:
      text_date: (str) date/time coordinate as present in input.
    Returns:
      (datetime) representation of input.
    """
    # Some records end with a question mark, because screw machine-readable!
    text_date = text_date.rstrip('?')
    # Some records have only minute precision, because of course they do!
    if text_date[-3] != ':':
        text_date = text_date + ':00'
    return datetime.strptime(text_date, '%Y %b %d %H%M:%S')


def load_launches(input_name, satellite_data):
    """Loads launch site data.

    Args:
      input_name: (str) fully qualified path name of corresponding input file
      satellite_data: (dict) actual satellite data as returned by
                      load_satellites().
    Returns:
      (tuple) of launch vehicle type index and actual launch data.
    """
    launches = {}
    types = set([])
    last_id = ''
    # We need to parse English month names in the input, so we make sure the
    # relevant system libraries will expect English input as well.
    old_locale = locale.setlocale(locale.LC_TIME, 'C')
    # Back to fixed-width, oh boy :-(
    with open(input_name, 'rt') as input_file:
        for input_line in input_file:
            if input_line[0] == '#':
                # Skip over headers, if present
                continue
            launch_id = input_line[0:13].strip()
            if launch_id:
                last_id = launch_id
                types.add(input_line[121:144].strip())
                launches[launch_id] = {
                    'datetime': parse_datetime(input_line[13:34].strip()),
                    'launchVehicleTypeID': input_line[121:144].strip(),
                    'launchVehicleSerial': input_line[144:160].strip(),
                    'siteID': input_line[160:169].strip(),
                    'launchPad': input_line[169:193].strip(),
                    # Coerce 'unknown' to 'failed'
                    'outcome': {
                        'S': True, 'F': False, 'U': False}[input_line[193]],
                    'reference': input_line[198:].strip()}
            satellite_id = prepend_extra_zero(input_line[112:121].strip())
            if satellite_id in satellite_data:
                satellite_data[satellite_id]['launchID'] = last_id
    locale.setlocale(locale.LC_TIME, old_locale)
    _LOG.info('Loaded launch data.')
    return (types, launches)


def to_normal_form(dataset, fields):
    """Brings tabular datasets to the normal form.

    Args:
      dataset: (dict) dataset to transform
      fields: (dict) indexes for all fields that should be extracted.
    Returns:
      (tuple) of the normalized dataset and the enumerated indexes.
    """
    # Generate indexes first ...
    indexes = {}
    for field in fields:
        indexes[field] = {x: y for y, x in enumerate(fields[field], start=1)}
    # ... then bring the dataset to normal form
    for key in dataset:
        for field in fields:
            dataset[key][field] = indexes[field][dataset[key][field]]
    return (dataset, indexes)


def print_for_sql(value):
    """Formats values for use with SQL."""
    if value is None:
        return 'NULL'
    if isinstance(value, datetime):
        return repr(value.strftime('%Y-%m-%d %H:%M:%S'))
    if isinstance(value, date):
        return repr(value.strftime('%Y-%m-%d'))
    return repr(value)


def generate_sql(table_name, data, output):
    """Generates SQL INSERT statements from input data.

    Args:
      table_name: (str) name of table to generate SQL INSERTs for
      data: (dict) input data
      output: (file)-like object SQL output will be written to.
    """
    for key, value in iteritems(data):
        output.write('INSERT INTO %s ' % table_name)
        if isinstance(value, dict):
            output.write('(id, %s) VALUES (' % ', '.join(value.keys()))
            output.write('%s, ' % repr(key))
            output.write('%s);\n' % ', '.join(
                (print_for_sql(x) for x in value.values())))
        else:
            output.write('VALUES (%s, %s);\n' % (repr(value), repr(key)))


def main(unused_argv):
    arguments = _FLAGS.parse_args()

    if arguments.output == '-':
        output_file = sys.stdout
    else:
        output_file = open(arguments.output, 'wt')
    if arguments.adddrop:
        add_drop(output_file)

    ensure_present(
        os.path.join(arguments.datadir, arguments.satellitelist),
        _INPUT_SOURCES[_FILE_SATELLITE], arguments.download, arguments.update)
    ensure_present(
        os.path.join(arguments.datadir, arguments.sitelist),
        _INPUT_SOURCES[_FILE_SITE], arguments.download, arguments.update)
    ensure_present(
        os.path.join(arguments.datadir, arguments.orbitalist),
        _INPUT_SOURCES[_FILE_ORBITAL], arguments.download, arguments.update)

    type_index, country_index, operator_index, sites = load_sites(
        os.path.join(arguments.datadir, arguments.sitelist))
    sites, site_indexes = to_normal_form(sites, {
        'typeID': type_index,
        'countryID': country_index,
        'operatorID': operator_index})

    owner_index, status_index, class_index, satellites = load_satellites(
        os.path.join(arguments.datadir, arguments.satellitelist))
    satellites, satellite_indexes = to_normal_form(satellites, {
        'ownerID': owner_index,
        'statusID': status_index,
        'orbitClassID': class_index})

    lvtype_index, launches = load_launches(
        os.path.join(arguments.datadir, arguments.orbitalist), satellites)
    launches, launch_indexes = to_normal_form(launches, {
        'launchVehicleTypeID': lvtype_index})

    # We only want satellites for which we have launch data, filter the rest.
    satellites = {
        x: y for x, y in iteritems(satellites)
        if y['launchID'] is not None}

    generate_sql('index_SiteType', site_indexes['typeID'], output_file)
    generate_sql('index_SiteCountry', site_indexes['countryID'], output_file)
    generate_sql('index_SiteOperator', site_indexes['operatorID'], output_file)
    generate_sql('index_Site', sites, output_file)
    generate_sql(
        'index_LaunchVehicleType', launch_indexes['launchVehicleTypeID'],
        output_file)
    generate_sql(
        'index_SatelliteOrbitClass', satellite_indexes['orbitClassID'],
        output_file)
    generate_sql(
        'index_SatelliteStatus', satellite_indexes['statusID'], output_file)
    generate_sql(
        'index_SatelliteOwner', satellite_indexes['ownerID'], output_file)
    generate_sql('data_Launch', launches, output_file)
    generate_sql('data_Satellite', satellites, output_file)

    output_file.close()


if __name__ == '__main__':
    main(sys.argv)
