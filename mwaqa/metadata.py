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
            u += "&dict"
        self.url = u

    def make_query(self, warn=True):
        if not hasattr(self, "url"):
            self.params2url()

        try:
            results = json.load(urlopen(self.url))
        except HTTPError as error:
            raise RuntimeError("HTTP error from server: code=%d" % error.code)
        except URLError as error:
            raise ValueError("URL or network error: %s" % error.reason)

        # Warn if we've hit the pagesize limit of results.
        if warn and len(results) >= self.params["pagesize"]:
            print("Query results may be truncated due to the pagesize parameter.",
                  file=sys.stderr)

        if self.extended:
            columns = (('local_sidereal_time_deg', "LST [deg]"),
                       ('mwas.creator', "Creator"),
                       ('mwas.dataquality', "Data Quality"),
                       ('mwas.dataqualitycomment', "Data Quality Comment"),
                       ('mwas.dec_phase_center', "Pointing Dec [deg]"),
                       ('mwas.freq_res', "Freq. Res. [kHz]"),
                       ('mwas.int_time', "Int. Time [s]"),
                       ('mwas.mode', "Mode"),
                       ('mwas.obsname', "Obs. Name"),
                       ('mwas.projectid', "ProjectID"),
                       ('mwas.ra_phase_center', "Pointing RA [deg]"),
                       ('mwas.starttime', "Obsid"),
                       ('mwas.stoptime', "Stop Time"),
                       ('numfiles', "Num. Files"),
                       ('rfs.frequencies', "Freq. Chans"),
                       ('sm.azimuth_pointing', "Azimuth [deg]"),
                       ('sm.dec_pointing', "Dec [deg]"),
                       ('sm.elevation_pointing', "Elevation [deg]"),
                       ('sm.gridpoint_number', "Gridpoint"),
                       ('sm.ra_pointing', "RA [deg]"))

            # astropy doesn't know how to format the "Freq. Chans" column of the
            # metadata (a list of ints for each frequency of the coarse-band
            # channels). Just turn it into a string.
            for r in results:
                r["rfs.frequencies"] = str(r["rfs.frequencies"])
            self.table = Table(results)
            self.table.rename_columns(*list(zip(*columns)))
            self.table = self.table["Obsid",
                                    "Stop Time",
                                    "Creator",
                                    "ProjectID",
                                    "Obs. Name",
                                    "RA [deg]",
                                    "Dec [deg]",
                                    "Pointing RA [deg]",
                                    "Pointing Dec [deg]",
                                    "Azimuth [deg]",
                                    "Elevation [deg]",
                                    "Gridpoint",
                                    "LST [deg]",
                                    "Freq. Res. [kHz]",
                                    "Int. Time [s]",
                                    "Mode",
                                    "Num. Files",
                                    "Freq. Chans",
                                    "Data Quality",
                                    "Data Quality Comment",
                                    ]
        else:
            columns = ("Obsid",
                       "Obs. Name",
                       "Creator",
                       "ProjectID",
                       "RA [deg]",
                       "Dec [deg]")
            self.table = Table(np.array(results), names=columns)

    def write_csv(self, output_filename):
        ap_ascii.write(self.table,
                       output_filename,
                       overwrite=True,
                       delimiter=',')
