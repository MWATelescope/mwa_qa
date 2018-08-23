#!/usr/bin/env python

# Python 2 and 3 compatibility
from __future__ import print_function, division
from future.builtins import range, str

import sys
import argparse

import numpy as np
from astropy.table import Table
from astropy.io import ascii as ap_ascii

import mwaqa.util as u


def query(args,
          columns=("obsid", "projectid", "lowest_channel", "eor_field", "iono_qa"),
          limit=100,
          actual_obsids=None):
    if args.obsid:
        results = u.select(constraints=("=", "obsid", args.obsid),
                           column_list=columns,
                           limit=limit)

    if args.min and args.max:
        results = u.select(constraints=("and",
                                        (">=", "obsid", args.min),
                                        ("<=", "obsid", args.max)),
                           column_list=columns,
                           limit=limit)

    # If actual_obsids is specified, then prune obsids that do not belong.
    if actual_obsids is not None:
        to_be_deleted = []
        for i, row in enumerate(results["rows"]):
            obsid = row[0]
            if obsid not in actual_obsids:
                to_be_deleted.append(i)
        for i in reversed(to_be_deleted):
            del results["rows"][i]

    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--obsid", type=int,
                        help="Extract the row for a single observation.")
    parser.add_argument("--min", type=int,
                        help="Use this parameter to specify the earliest obsid in a range.")
    parser.add_argument("--max", type=int,
                        help="Use this parameter to specify the latest obsid in a range.")
    parser.add_argument("--obsid_file", type=str,
                        help="Use this parameter to specify a file of obsids.")
    parser.add_argument("-l", "--limit", type=int, default=100,
                        help="The upper limit of results returned. Default: %(default)s")
    parser.add_argument("--csv", action="store_true",
                        help="Print results in a CSV format.")
    parser.add_argument("-f", "--output_filename", type=str, default=None,
                        help="If specified, write the query results as a CSV to the specified file. By default, results are printed to screen.")
    parser.add_argument("--delimiter", type=str, default=',',
                        help="Use this delimiter when printing CSV tables.")
    parser.add_argument("--projectid", action="store_false",
                        help="Print the projectid column. Default: %(default)s")
    parser.add_argument("--lowest_channel", action="store_false",
                        help="Print the lowest_channel column. Default: %(default)s")
    parser.add_argument("-e", "--eor_field", action="store_false",
                        help="Print the eor_field column. Default: %(default)s")
    parser.add_argument("-g", "--gridpoint_number", action="store_false",
                        help="Print the gridpoint_number column. Default: %(default)s")
    parser.add_argument("-i", "--iono_qa", action="store_false",
                        help="Print the iono_qa column. Default: %(default)s")
    parser.add_argument("-m", "--iono_mag", action="store_true",
                        help="Print the iono_mag column. Default: %(default)s")
    parser.add_argument("-p", "--iono_pca", action="store_true",
                        help="Print the iono_pca column. Default: %(default)s")
    parser.add_argument("-s", "--sourcelist", action="store_true",
                        help="Print the sourcelist column. Default: %(default)s")
    parser.add_argument("-u", "--uvfits_path", action="store_true",
                        help="Print the uvfits_path column. Default: %(default)s")
    args = parser.parse_args()

    # Checking that arguments are sensible.
    if args.obsid or args.obsid_file:
        if args.min or args.max:
            print("Cannot combine --min or --max with --obsid or --obsid_file",
                  file=sys.stderr)
            exit(1)

    if args.obsid and args.obsid_file:
        print("Cannot combine --obsid with --obsid_file",
              file=sys.stderr)
        exit(1)

    if (args.min and not args.max) or (args.max and not args.min):
        print("Both the minimum and maximum of a range search are required.",
              file=sys.stderr)
        exit(1)

    # Print in a CSV format if the output_filename argument is set.
    if (not args.csv and args.output_filename):
        args.csv = True

    if args.output_filename is None:
        args.output_filename = sys.stdout

    # Make it possible to use tabs as delimiters from the command line.
    if args.delimiter == "\\t":
        args.delimiter = "\t"

    columns = ["obsid", "projectid", "lowest_channel", "eor_field", "gridpoint_number", "iono_qa"]
    column_dict = {
        "iono_magnitude": args.iono_mag,
        "iono_pca": args.iono_pca,
        "sourcelist": args.sourcelist,
        "uvfits_path": args.uvfits_path,
    }
    for k, v in column_dict.items():
        if v:
            columns.append(k)

    # If we've been passed a file, just query all obsids between the
    # minimum and maximum inside the file, then prune the ones not in the file.
    if args.obsid_file:
        obsids = np.loadtxt(args.obsid_file, dtype=int)
        args.min = np.min(obsids).astype(str)
        args.max = np.max(obsids).astype(str)
        results = query(args, columns=columns, limit=100000000, actual_obsids=obsids)
    else:
        results = query(args, columns=columns, limit=args.limit)

    t = Table(np.array(results["rows"]), names=columns)
    if args.csv:
        ap_ascii.write(t,
                       args.output_filename,
                       overwrite=True,
                       delimiter=args.delimiter)
    else:
        t.pprint(max_lines=-1, max_width=-1)
