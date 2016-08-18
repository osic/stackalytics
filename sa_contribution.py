#! /usr/bin/env python3
import argparse
import csv
import sys
import json
from datetime import datetime
from urllib import request, parse, error

import pytz

app_desc = """
StackAlytics Contribution Puller

This utility retrieves OpenStack contributions in CSV format, given
an input file of launchpad ids (one id per line).  Additional tokens
in a csv-formatted input file will be safely ignored (letting you use
the same file with sa_grouper.py for subtotals).  If you don't specify
this file, the program will look for launchpad_ids.csv in the current
directory.

The CSV output goes to stdout by default, but an output file name can
also be specified.

You can filter by OpenStack release name and/or a date range.  If you
specify neither, you'll get the date range spanning from July 23, 2015
(the birthday of OSIC) to today.
"""

# -------- GLOBAL DEEFAULTS ------------------------------------

DEFAULT_ID_LIST = "./launchpad_ids.csv"
DEFAULT_START_DATE = '20150723' #Birthdate of OSIC

# Base URL being accessed
BASE_URL = 'http://stackalytics.com/api/1.0/contribution'

# ---------------------------------------------------------------


def tally_reviews(marks):
    """The API call above returns a set of "marks", representing code reviews
    for each of the possible scores (e.g., -2, -1, 0, 1, 2, etc.).
    This function simply adds them all together and returns total code reviews
    """
    total = 0
    for i in marks.values():
        total += i
    return total

def unix_time_for_date(date_string, end_of_day=False):
    """Returns a UNIX time representing midnight on the day specified in YYYYMMDD format.
    If end_of_day == True, the time will represent the end of day (23:59:59) instead of its
    start.
    """
    try:
        if len(date_string) != 8:
            raise ValueError()
        result_time=(0,0,0)
        if end_of_day:
            result_time = (23,59,59)

        result_date = datetime(int(date_string[0:4]),int(date_string[4:6]),int(date_string[6:8]),
                               result_time[0],result_time[1],result_time[2],0,pytz.utc)
    except (ValueError):
        raise ValueError("Date must be of the format YYYYMMDD")

    return int(result_date.timestamp())

def pull_contributions(start_date: str, end_date: str, release_name: str,
                       idfile_name: str, outfile_name: str):

    # Put the id_list in memory, so we don't have to re-read the id file on each
    # cycle
    lpad_ids = []
    with open(idfile_name) as ids:
        csvreader = csv.reader(ids)
        for row in csvreader:
            lpad_ids.append(row[0])

    results = []
    parms = {}
    if start_date:
        parms['start_date'] = str(unix_time_for_date(start_date, False))

    if end_date:
        parms['end_date'] = str(unix_time_for_date(end_date, True))

    if release_name:
        parms['release'] = release_name.lower()

    print("\nQuerying {0} ids...".format(len(lpad_ids)), file=sys.stderr)

    for lpad_id in lpad_ids:

        # Dictionary of query parameters (if any)
        parms ['user_id'] = lpad_id.strip()

        # Encode the query string
        querystring = parse.urlencode(parms)

        # Make a GET request and read the response
        try:
            u = request.urlopen(BASE_URL + '?' + querystring)
            contribution = json.loads(u.read().decode(encoding='UTF-8'))['contribution']

            row = (
                lpad_id.strip(),
                contribution['change_request_count'],
                contribution['commit_count'],
                contribution['completed_blueprint_count'],
                contribution['drafted_blueprint_count'],
                contribution['email_count'],
                contribution['loc'],
                tally_reviews(contribution['marks']),
                contribution['patch_set_count'],
                contribution['resolved_bug_count'],
            )
            results.append(row)

        except error.HTTPError:
            print("Couldn't retrieve data for user: " + lpad_id.strip(), file=sys.stderr)
        except:
            raise

    # Write output CSV file
    if outfile_name is None:
        outfile = sys.stdout
    else:
        outfile = open(outfile_name, 'w')

    if not outfile:
        raise FileNotFoundError("Couldn't open output file")

    print("\nWriting output file", file=sys.stderr)
    fieldnames = ['user_id',
                  'change_requests',
                  'commits',
                  'blueprint_cmpl',
                  'blueprint_draft',
                  'email',
                  'loc',
                  'reviews',
                  'patch_sets',
                  'bug_fixes',
                  ]

    writer = csv.writer(outfile)
    writer.writerow(fieldnames)
    writer.writerows(results)

    outfile.close()


if __name__ == '__main__':


    parser = argparse.ArgumentParser(description=app_desc)
    parser.add_argument('-s', '--start', dest='start_date', help='Start Date (YYYYMMDD)')
    parser.add_argument('-e', '--end', dest='end_date', help='End Date (YYYYMMDD)')
    parser.add_argument('-r', '--release', dest='release_name', help='OpenStack Release Name')
    parser.add_argument('-l', '--id-file', dest='idfile_name',
                        default='./launchpad_ids.csv',
                        help='Name of file containing launchpad ids (one per line)')
    parser.add_argument('-o', '--output', dest='outfile_name',
                        help='Output CSV file name (defaults to stdout)')

    args = parser.parse_args()

    if args.start_date is None and args.end_date is not None:
        args.start_date = DEFAULT_START_DATE
        print("Using default start date of {0}".format(DEFAULT_START_DATE), file=sys.stderr)

    now = datetime.today()
    today_string = '{0}{1:02}{2:02}'.format(now.year, now.month, now.day)
    if args.end_date is None and args.start_date is not None:
        args.end_date = today_string
        print("Using default end date of today", file=sys.stderr)

    # Note that specifying the release without any dates will not trigger defaults
    if not any([args.start_date, args.end_date, args.release_name]):
        args.start_date = DEFAULT_START_DATE
        print("Using default start date of {0}".format(DEFAULT_START_DATE), file=sys.stderr)
        args.end_date = today_string
        print("Using default end date of today", file=sys.stderr)

    pull_contributions(args.start_date, args.end_date, args.release_name,
                       args.idfile_name, args.outfile_name)
