#!/usr/bin/env python

from __future__ import print_function
from future.builtins import range

import sys
import json
import argparse

import numpy as np
from astropy.table import Table
from astropy.io import ascii as ap_ascii

# Python3
try:
    from urllib.parse import urlencode
    from urllib.request import urlopen
    from urllib.error import HTTPError, URLError

# Python2
except ImportError:
    from urllib import urlencode
    from urllib2 import urlopen, HTTPError, URLError


def get_complete_parameters():
    return {"pagesize": 10,
            "projectid": "",
            "obsname": "",
            "creator": "",
            "mintime": "",
            "maxtime": "",
            "mintime_utc": "",
            "maxtime_utc": "",
            "minra": "",
            "maxra": "",
            "mindec": "",
            "maxdec": "",
            "minel": "",
            "maxel": "",
            "minaz": "",
            "maxaz": "",
            "gridpoint": "",
            "minlst": "",
            "maxlst": "",
            "minsunel": "",
            "maxsunel": "",
            "minsunpd": "",
            "maxsunpd": "",
            "mode": "",
            "cenchan": "",
            "anychan": "",
            "freqres": "",
            "inttime": "",
            "minfiles": ""}

class Query(object):
    def __init__(self, extended_results=True):
        self.extended = extended_results
        self.params = get_complete_parameters()

    def params2url(self):
        u = "{0}&{1}".format("http://mro.mwa128t.org/metadata/find/?search=search",
                             urlencode(self.params))
        if self.extended:
            u += "&extended"
        self.url = u

    def results(self, csv=False, output_filename=None):
        self.csv = csv

        if not hasattr(self, "url"):
            self.params2url()

        try:
            results = json.load(urlopen(self.url))
        except HTTPError as error:
            raise RuntimeError("HTTP error from server: code=%d" % error.code)
        except URLError as error:
            raise ValueError("URL or network error: %s" % error.reason)

        if self.extended:
            columns = ("Obsid",
                       "End time",
                       "Obs Name",
                       "Creator",
                       "ProjectID",
                       "Right Ascension [deg]",
                       "Declination [deg]",
                       "Azimuth [deg]",
                       "Elevation [deg]",
                       "Pointing RA [deg]",
                       "Pointing Dec [deg]",
                       "LST [deg]")
        else:
            columns = ("Obsid",
                       "Obs Name",
                       "Creator",
                       "ProjectID",
                       "Right Ascension [deg]",
                       "Declination [deg]")

        # Warn if we've hit the pagesize limit of results.
        if len(results) >= self.params["pagesize"]:
            print("Query results may be truncated due to the pagesize parameter.",
                  file=sys.stderr)

        self.table = Table(np.array(results), names=columns)
        if self.csv:
            if output_filename is None:
                raise ValueError("No output filename specified!")
            ap_ascii.write(self.table,
                           output_filename,
                           overwrite=True,
                           delimiter=',')
        else:
            self.table.pprint(max_lines=-1, max_width=-1)

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
    parser.add_argument("--output_filename", type=str, default=sys.stdout,
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
    # Handle the results; this prints the table to stdout, or writes the contents to a specified filename.
    q.results(csv=args.csv, output_filename=args.output_filename)
