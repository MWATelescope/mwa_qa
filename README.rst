mwaqa
=====

Scripts and utilities to interface with the MWA quality assurance (QA) database.

Example usage
-------------
As a demonstration and convenience, the ``mwaqa_query.py`` script is available. It is possible to query specific observations::

  mwaqa_query.py -o 1065880128

or a range::

  mwaqa_query.py --min 1065880000 --max 1065881000

or obsids from a file::

  mwaqa_query.py --obsid_file /path/to/obsids.txt

It is possible to add columns to or remove columns from the query's results, such as ``iono_magnitude`` or ``sourcelist``. All supported modifications are detailed in the help::

  mwaqa_query -h

Finally, it is possible to print query results as a CSV using the ``--csv`` flag, and write the query results directly into a file with the ``-f`` flag.

General usage
-------------
More flexibility is provided by the ``mwaqa.utils`` library file. For example, to print the ``uvfits_path`` column for all obsids with a ``gridpoint_number`` of `-1`::

  import numpy as np
  from astropy.table import Table

  import mwaqa.util as u

  columns = ("obsid", "projectid", "lowest_channel", "eor_field", "gridpoint_number", "iono_qa", "uvfits_path")

  # Select all obsids from the database with gridpoint_number -1.
  qa_db_results = u.select(constraints=("and",
                                        ("and",
                                         ("and",
                                          (">=", "obsid", 1),
                                          ("<=", "obsid", 3000000000)),
                                         ("=", "gridpoint_number", -1)),
                                        ("like", "uvfits_path", "%")), # This rule means "non blank"
                           column_list=columns,
                           limit=1000000)

  # Convert Andrew's output to an astropy table.
  t = Table(np.array(qa_db_results["rows"]), names=columns)

  # Print uvfits_path for each obsid.
  for path in t["uvfits_path"]:
      print(path)

To print the whole table with the ``columns`` specified, ``astropy``'s table has a useful ``pprint`` method::

  # Print the table for inspection.
  t.pprint(max_lines=-1, max_width=-1)

Limitations
-----------
The code hosted by this repo utilises Andrew Williams' JSON web querying backend. This backend has support for database row deletion, addition and alteration, but any modifications of the QA database require privileged access.

Bugs? Inconsistencies?
----------------------
If you find something odd, raise an issue and we'll attempt to fix it ASAP.

Contact
-------
christopherjordan87 -at- gmail.com

Dependencies
------------
- python 2.7.x or 3.x
- numpy
- astropy
- future

Installation
------------
1. Clone this repository
2. Run ``pip install .`` inside the repo.

or

1. Clone this repository
2. Add the path to this repository to your PYTHONPATH
3. Add this repository's ``scripts`` path to your PATH
