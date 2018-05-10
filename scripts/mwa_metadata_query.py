#!/usr/bin/env python

# Python 2 and 3 compatibility
from __future__ import print_function
from future.builtins import range, str

import sys
import argparse

from astropy.io import ascii as ap_ascii

from mwaqa.metadata import Query


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pagesize", type=int, default=100,
                        help="Specify limit of results to return from the query. Default: %(default)s")
    parser.add_argument("--projectid", type=str,
                        help="Project ID. e.g. G0009")
    parser.add_argument("--obsname", type=str,
                        help="Observation name. e.g. high_season%")
    parser.add_argument("--creator", type=str,
                        help="Name of the creator. e.g. DJacobs")
    parser.add_argument("--mintime", type=int, default=1065880000,
                        help="Minimum start time. e.g. 1065880000")
    parser.add_argument("--maxtime", type=int, default=1065881000,
                        help="Maximum start time. e.g. 1065881000")
    parser.add_argument("--mintime_utc", type=str,
                        help="Minimum UTC time.")
    parser.add_argument("--maxtime_utc", type=str,
                        help="Maximum UTC time.")
    parser.add_argument("--minra", type=float,
                        help="The minimum RA of the observations in degrees. e.g. 0.0")
    parser.add_argument("--maxra", type=float,
                        help="The maximum RA of the observations in degrees. e.g. 0.0")
    parser.add_argument("--mindec", type=float,
                        help="The minimum RA of the observations in degrees. e.g. -27.0")
    parser.add_argument("--maxdec", type=float,
                        help="The maximum RA of the observations in degrees. e.g. -27.0")
    parser.add_argument("--minel", type=float,
                        help="Minimum elevation in degrees. e.g. 80.0")
    parser.add_argument("--maxel", type=float,
                        help="Maximum elevation in degrees. e.g. 90.0")
    parser.add_argument("--minaz", type=float,
                        help="Minimum azimuth in degrees.")
    parser.add_argument("--maxaz", type=float,
                        help="Maximum elevation in degrees.")
    parser.add_argument("--gridpoint", type=int,
                        help="MWA gridpoint.")
    parser.add_argument("--cenchan", type=int,
                        help="Centre channel. e.g. 143 or 121")
    parser.add_argument("--inttime", type=float,
                        help="Integration time in seconds. e.g. 0.5")
    parser.add_argument("--minfiles", type=int,
                        help="Minimum number of files. e.g. 25")
    parser.add_argument("--csv", action="store_true",
                        help="Return results in a CSV format.")
    parser.add_argument("--output_filename", type=str,
                        help="The filename where CSV results are to be written. Default: %(default)s")
    parser.add_argument("--brief", action="store_true",
                        help="Return only a few columns (disables the \"extended\" feature).")
    args = parser.parse_args()

    # Parameters not related to the MWA metadata service.
    unrelated = ["csv", "output_filename", "brief"]

    # Create a query object.
    q = Query(extended_results=not args.brief)

    # Populate the parameters of the query with whatever's been specified via argparse.
    for arg in vars(args):
        if arg in unrelated:
            continue
        elif getattr(args, arg) is not None:
            q.params[arg] = getattr(args, arg)

    # Make the query.
    q.make_query()

    # If the output_filename has been specified, then we don't need to print the
    # query results, only write them to a file.
    if args.output_filename:
        q.write_csv(output_filename=args.output_filename)
    # Otherwise, handle the printing.
    else:
        if args.csv:
            ap_ascii.write(q.table,
                           sys.stdout,
                           delimiter=',')
        else:
            q.table.pprint(max_lines=-1, max_width=-1)
