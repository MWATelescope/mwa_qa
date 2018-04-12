mwaqa
=====

Scripts and utilities to interface with the MWA quality assurance (QA) database.

Usage
-----
At present, only the ``mwaqa_query.py`` script is available. It is possible to query specific observations::

  mwaqa_query.py -o 1065880128

or a range::

  mwaqa_query.py --min 1065880000 --max 1065881000

or obsids from a file::

  mwaqa_query.py --obsid_file /path/to/obsids.txt

It is possible to add columns to or remove columns from the query's results, such as ``iono_magnitude`` or ``sourcelist``. All supported modifications are detailed in the help::

  mwaqa_query -h

Finally, it is possible to print query results as a CSV using the ``--csv`` flag, and put the query results directly into a file with the ``-f`` flag.

Limitations
-----------
The code hosted by this repo utilises Andrew Williams' JSON web querying backend. This backend has support for database row deletion, addition and alteration, but these features are currently unavailable here.

Bugs? Inconsistencies?
----------------------
If you find something odd, let us know and we'll attempt to fix it ASAP.

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
- Clone this repository
- Add the path to this repository to your PYTHONPATH
- Add this repository's ``scripts`` path to your PATH
