# Python 2 and 3 compatibility
from __future__ import print_function
from future.builtins import range, str

import sys
import json

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


def complete_parameters():
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
    def __init__(self, extended_results=True, pagesize=10):
        self.extended = extended_results
        self.params = complete_parameters()
        self.params["pagesize"] = pagesize

    def params2url(self):
        u = "{0}&{1}".format("http://mro.mwa128t.org/metadata/find/?search=search",
                             urlencode(self.params))
        if self.extended:
            u += "&extended"
        self.url = u

    def make_query(self):
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

    def write_csv(self, output_filename):
        ap_ascii.write(self.table,
                       output_filename,
                       overwrite=True,
                       delimiter=',')
