#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Import historical orbital launch data into an SQL database.

   Copyright (C) 2020 Claudiu Tănăselia <your email here>.

   Released under the <your licence here>.
"""
import argparse
import csv
from datetime import datetime
import locale
import logging
import os
import sys
from urllib.request import urlretrieve

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
    '--adddrop', default=False,
    help='Prepend DROP/CREATE TABLE statements to the output.',
    action='store_true')
_LOG = logging.getLogger(__name__)

_FILE_ORBITAL = 1
_FILE_SATELLITE = 2
_FILE_SITE = 3
_INPUT_SOURCES = {
    _FILE_ORBITAL: 'https://www.planet4589.org/space/log/launchlogy.txt',
    _FILE_SATELLITE: 'https://www.planet4589.org/space/log/satcat.txt',
    _FILE_SITE: 'https://www.planet4589.org/space/gcat/data/tables/sites.tsv'}


def add_drop(output):
    output.write(
        """DROP TABLE satellites;
DROP TABLE launches;
""")

    output.write(
        """CREATE TABLE launches (
launchID TEXT,
launchDate TIMESTAMP,
COSPAR TEXT,
postPayload TEXT,
prePayload TEXT,
SATCAT TEXT,
LV_type TEXT,
LV_serial TEXT,
launchSite TEXT,
launchPad TEXT,
lsState TEXT,
outcome TEXT);
""")

    output.write(
        """CREATE TABLE satellites (
launchID TEXT,
COSPAR TEXT,
postPayload TEXT,
prePayload TEXT,
owner TEXT,
SATCAT TEXT,
orbitPrd TEXT,
orbitClass TEXT,
orbitPAI TEXT);
""")


def ensure_present(input_name, input_type, fetch_input):
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
            _ = urlretrieve(_INPUT_SOURCES[input_type], input_name)
    else:
        if not os.access(input_name, os.R_OK):
            _LOG.fatal(
                'Input file "%s" exists but is not readable, cannot continue! ',
                input_name)
    _LOG.info('Input file "%s" present and readable.', input_name)


def parse_date(text_date, start_date):
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
    try:
        return float(text_float)
    except ValueError:
        return float('NaN')


def load_satellites(input_name):
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
                'COSPAR': input_line[8:23].strip(),
                'initialName': input_line[23:64].strip(),
                'finalName': input_line[64:89].strip(),
                'owner': input_line[89:102].strip(),
                'status': input_line[114:131].strip(),
                'statusDate': parse_date(input_line[131:144].strip(), True),
                'orbitEpoch': parse_date(input_line[144:156].strip(), True),
                'orbitClass': input_line[156:165].strip(),
                'orbitPeriod': parse_float(input_line[165:174].strip()),
                'orbitPerigee': parse_float(input_line[174:181].strip()),
                'orbitApogee': parse_float(input_line[183:190].strip()),
                'orbitInclination': parse_float(input_line[192:198].strip())}
    _LOG.info('Loaded satellite data.')
    locale.setlocale(locale.LC_TIME, old_locale)
    return (owners, statuses, classes, satellites)


def load_sites(input_name):
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
            countries.add(input_record[4])
            operators.add(input_record[13])
            sites[input_record[0]] = {
                'type': input_record[3],
                'country': input_record[4],
                'dateStart': parse_date(input_record[5], True),
                'dateEnd': parse_date(input_record[6], False),
                'shortName': input_record[7],
                'fullName': input_record[8],
                'locationName': input_record[9],
                'locationLat': parse_float(input_record[10]),
                'locationLon': parse_float(input_record[11]),
                'locationError': float(input_record[12]),
                'operator': input_record[13]}
    locale.setlocale(locale.LC_TIME, old_locale)
    _LOG.info('Loaded launch site data.')
    return (types, countries, operators, sites)


def prepend_extra_zero(satcat):
    return satcat[0] + '0' + satcat[1:]


def parse_datetime(text_date):
    # Some records end with a question mark, because screw machine-readable!
    text_date = text_date.rstrip('?')
    # Some records have only minute precision, because of course they do!
    if text_date[-3] != ':':
        text_date = text_date + ':00'
    return datetime.strptime(text_date, '%Y %b %d %H%M:%S')


def load_launches(input_name, satellite_data):
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
                    'lvType': input_line[121:144].strip(),
                    'lvSerial': input_line[144:160].strip(),
                    'launchSiteID': input_line[160:169].strip(),
                    'launchPad': input_line[169:193].strip(),
                    'outcome': {'S': True, 'F': False}[input_line[193]],
                    'reference': input_line[198:].strip()}
            satellite_data[prepend_extra_zero(
                input_line[112:121].strip())]['launchID'] = last_id
    locale.setlocale(locale.LC_TIME, old_locale)
    _LOG.info('Loaded launch data.')
    return launches


def to_normal_form(dataset, fields):
    # Generate indexes first ...
    indexes = {}
    for field in fields:
        indexes[field] = {x: y for y, x in enumerate(fields[field])}
    # ... then bring the dataset to normal form
    for key in dataset:
        for field in fields:
            dataset[key][field] = indexes[field][dataset[key][field]]
    return (dataset, indexes)


def generate_sql(output, launches, satellites, sites):
    for launch in launches:
        output.write(
            """INSERT INTO launches VALUES (
'%(id)s', '%(datetime)s', '%(COSPAR)s', '%(postPayload)s', '%(prePayload)s',
'%(SATCAT)s', '%(LV_type)s', '%(LV_serial)s', '%(launchSite)s', '%(launchPad)s',
'%(sitelocation)s', '%(outcome)s');
""" % {
    'id': launch,
    'datetime': launches[launch]['datetime'].isoformat(),
    'COSPAR': launches[launch]['COSPAR'],
    'postPayload': launches[launch]['postPayload'],
    'prePayload': launches[launch]['prePayload'],
    'SATCAT': launches[launch]['SATCAT'],
    'LV_type': launches[launch]['LV_type'],
    'LV_serial': launches[launch]['LV_serial'],
    'launchSite': launches[launch]['launchSite'],
    'launchPad': launches[launch]['launchPad'],
    'sitelocation': sites[launches[launch]['launchSite']],
    'outcome': launches[launch]['outcome']})


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
        _FILE_SATELLITE, arguments.download)
    ensure_present(
        os.path.join(arguments.datadir, arguments.sitelist), _FILE_SITE,
        arguments.download)
    ensure_present(
        os.path.join(arguments.datadir, arguments.orbitalist), _FILE_ORBITAL,
        arguments.download)

    type_index, country_index, operator_index, sites = load_sites(
        os.path.join(arguments.datadir, arguments.sitelist))
    sites, site_indexes = to_normal_form(sites, {
        'type': type_index,
        'country': country_index,
        'operator': operator_index})

    owner_index, status_index, class_index, satellites = load_satellites(
        os.path.join(arguments.datadir, arguments.satellitelist))
    satellites, satellite_indexes = to_normal_form(satellites, {
        'owner': owner_index,
        'status': status_index,
        'orbitClass': class_index})

    lvtype_index, launches = load_launches(
        os.path.join(arguments.datadir, arguments.orbitalist), satellites)
    launches, launch_indexes = to_normal_form(launches, {
        'lvType': lvtype_index})

    generate_sql(output_file, launches, satellites, sites)
    output_file.close()


if __name__ == '__main__':
    main(sys.argv)
