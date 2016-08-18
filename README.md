# Utilities for OpenStack Stackalytics Data

## StackAlytics Contribution Puller (sa_contribution.py)

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

```bash
usage: sa_contribution.py [-h] [-s START_DATE] [-e END_DATE] [-r RELEASE_NAME]
                          [-i IDFILE_NAME] [-o OUTFILE_NAME]

optional arguments:
  -h, --help            show this help message and exit
  -s START_DATE, --start START_DATE
                        Start Date (YYYYMMDD
  -e END_DATE, --end END_DATE
                        End Date (YYYYMMDD
  -r RELEASE_NAME, --release RELEASE_NAME
                        OpenStack Release Name
  -i IDFILE_NAME, --id-file IDFILE_NAME
                        Name of file containing launchpad ids
  -o OUTFILE_NAME, --output OUTFILE_NAME
                        Output CSV file name (defaults to stdout)
```

## StackAlytics ID Generator (sa_gen_id_lookup.py)

This utility takes no arguments.  It simply queries StackAlytics for
all ids associated with either "Intel" or "Rackspace" as a company
designation. The resulting launchpad ids and names are printed to stdout.

Note that this list is not the same as the list of OSIC participants.
It's just helpful for figuring out launchpad ids for folks.  Use the
launchpad_id column in the official OSIC Roster for pulling OSIC
contributions.


## Contribution Data Summarizer (sa_grouper.py)

(TBD) This utility takes the output of sa_contribution.py and generates
useful subtotals.  Not uploaded yet.
