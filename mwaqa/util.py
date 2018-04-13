# Python 2 and 3 compatibility
from __future__ import print_function, division
from future.builtins import range, str

import json
import logging

# Python3
try:
    from urllib.parse import urlencode
    from urllib.request import urlopen
    from urllib.error import HTTPError, URLError
    import configparser as ConfigParser
# Python2
except ImportError:
    from urllib import urlencode
    from urllib2 import urlopen, HTTPError, URLError
    import ConfigParser


# configure the logging
logging.basicConfig(format="# %(levelname)s:%(name)s: %(message)s")
logger = logging.getLogger("quality")

# This server only has read-only access to the table, only select queries will work.
BASEURL = "http://mwa-metadata01.pawsey.org.au/"
# Default user_name to use for queries, if user_name is not supplied.
DEFAULTID = "quality"
# Paths to search for the config file containing user names and passwords.
CPPATH = ["/usr/local/etc/quality.conf", "./quality.conf"]
# Placeholder for the user_name/secure_key global dictionary
KEYS = None


def getmeta(servicetype="metadata", service="obs", params=None):
    """
    Given a JSON web servicetype ('observation', 'metadata', 'quality', etc), a service name (eg 'obs', find, or 'con')
    and a set of parameters as a Python dictionary, return the result of calling that service.

    If the service returns a structure in JSON format, return the structure itself,
    otherwise return the result as a string.

    :param servicetype: Service type (the Django package name), eg 'quality'.
    :param service: Service name (the Django function), eg 'select'.
    :param params: A dictionary containing the name/value pairs to pass to the service call.
    :return: A Python object converted from a JSON string, or the raw string if it's not in JSON format.
    """
    if params:
        data = urlencode(params)  # Turn the dictionary into a string with encoded "name=value" pairs
    else:
        data = ""

    # Get the data
    returnstring = ""
    try:
        returnstring = urlopen(BASEURL + servicetype + '/' + service + '?' + data).read()
        result = json.loads(returnstring)
    except ValueError:   # Result isn't in JSON format
        result = returnstring
    except HTTPError as error:
        print("HTTP error from server: code=%d, response:\n %s" % (error.code, error.read()))
        return
    except URLError as error:
        print("URL or network error: %s" % error.reason)
        return
    # Return the result dictionary
    return result


def load_config_options():
    """
    Populate the KEYS global variable using the config file. This dictionary maps user names to secure keys (passwords).

    Providing a user_name and secure_key is necessary for the insert, update, and delete functions, but not for select.
    If you are writing to the database, you must use an appropriate BASEURL, and you must have a copy of the config
    file with at least one username/password pair that matches a valid user/password on the server.
    """
    global KEYS
    global BASEURL
    KEYS = {None:None}

    logger.debug("loading config file.")
    CP = ConfigParser.SafeConfigParser(defaults={})
    CPfile = CP.read(CPPATH)
    if not CPfile:
        logger.critical("None of the specified configuration files found by quality.py: %s" % (CPPATH,))
        return
    for user_name, key in CP.items(section="KEYS"):
        KEYS[user_name] = key.strip()
    for _, key in CP.items(section="BASEURL"):
        BASEURL = key.strip()
    logger.debug("Config file loaded, %d keys" % (len(KEYS),))


def insert(row=None, user_name=DEFAULTID, secure_key=None):
    """
    Call the insert() web service to insert the given data as one row.

    The function returns a dictionary contains any error messages, and the results of the call.
    It has the following key/value pairs:

    result['errors'] - A dictionary, containing integer keys, with values being any error messages (in order)
                       generated when processing that call.
    result['success'] - A Boolean, true for success or False if the call failed.
    result['query'] - The actual SQL query sent to the PostgreSQL server.

    :param row: A dictionary, with keys for the column names and values for the data to be inserted.
                The obsid column must be present.
    :param user_name: A project ID code (or a pseudo-ID) to authenticate against on the server for permission.
    :param secure_key: A password to match against the value on the server for the given user_name, for permission.
    :return: The result dictionary, described above.
    """
    if KEYS is None:
        load_config_options()

    if secure_key is None:
        secure_key = KEYS.get(user_name, "")

    if "mro" not in BASEURL:
        logger.critical("INSERT calls won't work unless BASEURL is set to the MRO server")
        return

    if not secure_key:
        logger.critical("INSERT calls won't work without a valid user_name and secure_key, check the config file.")
        return

    result = getmeta(servicetype="quality", service="insert", params={"row": json.dumps(row),
                                                                      "user_name": user_name,
                                                                      "secure_key": secure_key})
    return result


def update(constraints=None, data=None, user_name=DEFAULTID, secure_key=None):
    """
    Call the update() web service to change the contents of the rows matching the constraints.

    Constraints are passed as a nested heirarchy of tuples or lists, each defining an operator and its argument/s.
    Each list consists of:
        -An operator string, currently one of '=', '<', '<=', '>', '>=', '!=', 'and', 'or', 'not' or 'like'
        -An argument, which could be a string value, a numeric value, a column name, OR another constraint tuple.
        -Another argument, which could be a string value, a numeric value, a column name, OR another constraint tuple.

    In the case of a unary operator, the list has two elements - the operator and one argument. Currently, the only
    unary operator is 'not'.

    For example, this constraint:
        ('or',
            ('and',
                   ('>', 'obsid', 500),
                   ('<', 'obsid', 1000)),
            ('not',
                   ('like', 'projectid', '%000%')))

    Would translate to SQL looking like:
        WHERE (((obsid > 500) AND (obsid < 1000)) OR (NOT (projectid LIKE '%000%')))

    The function returns a dictionary contains any error messages, and the results of the call.
    It has the following key/value pairs:

    result['errors'] - A dictionary, containing integer keys, with values being any error messages (in order)
                       generated when processing that call.
    result['success'] - A Boolean, true for success or False if the call failed.
    result['query'] - The actual SQL query sent to the PostgreSQL server.
    result['rowcount'] - The number of rows matching the constraints provided.

    :param constraints: A nested list of constraints, in the format described above.
    :param data: A dictionary containg name/value pairs, where each 'name' is a column name in the quality table,
                 and the corresponding 'value' is the new contents for that column to be set in the rows matching the
                 given constraints.
    :param user_name: A project ID code (or a pseudo-ID) to authenticate against on the server for permission.
    :param secure_key: A password to match against the value on the server for the given user_name, for permission.
    :return: The result dictionary, described above.
    """
    if KEYS is None:
        load_config_options()

    if secure_key is None:
        secure_key = KEYS.get(user_name, "")

    if "mro" not in BASEURL or not secure_key:
        logger.critical("UPDATE calls won't work without a valid user_name and secure_key, check the config file.")
        return

    result = getmeta(servicetype="quality", service="update", params={"constraints": json.dumps(constraints),
                                                                      "data": json.dumps(data),
                                                                      "user_name": user_name,
                                                                      "secure_key": secure_key})
    return result


def delete(constraints=None, user_name=DEFAULTID, secure_key=None):
    """
    Call the delete() web service to delete the rows matching the constraints.

    Constraints are passed as a nested heirarchy of tuples or lists, each defining an operator and its argument/s.
    Each list consists of:
        -An operator string, currently one of '=', '<', '<=', '>', '>=', '!=', 'and', 'or', 'not' or 'like'
        -An argument, which could be a string value, a numeric value, a column name, OR another constraint tuple.
        -Another argument, which could be a string value, a numeric value, a column name, OR another constraint tuple.

    In the case of a unary operator, the list has two elements - the operator and one argument. Currently, the only
    unary operator is 'not'.

    For example, this constraint:
        ('or',
            ('and',
                ('>', 'obsid', 500),
                ('<', 'obsid', 1000)),
            ('not',
                ('like', 'projectid', '%000%')))

    Would translate to SQL looking like:
        WHERE (((obsid > 500) AND (obsid < 1000)) OR (NOT (projectid LIKE '%000%')))

    The function returns a dictionary contains any error messages, and the results of the call.
    It has the following key/value pairs:

    result['errors'] - A dictionary, containing integer keys, with values being any error messages (in order)
                       generated when processing that call.
    result['success'] - A Boolean, true for success or False if the call failed.
    result['query'] - The actual SQL query sent to the PostgreSQL server.
    result['rowcount'] - The number of rows deleted.

    :param constraints: A nested list of constraints, in the format described above.
    :param user_name: A project ID code (or a pseudo-ID) to authenticate against on the server for permission.
    :param secure_key: A password to match against the value on the server for the given user_name, for permission.
    :return: The result dictionary, described above.
    """
    if KEYS is None:
        load_config_options()

    if secure_key is None:
        secure_key = KEYS.get(user_name, "")

    if "mro" not in BASEURL or not secure_key:
        logger.critical("DELETE calls won't work without a valid user_name and secure_key, check the config file.")
        return

    result = getmeta(servicetype="quality", service="delete", params={"constraints": json.dumps(constraints),
                                                                      "user_name": user_name,
                                                                      "secure_key": secure_key})
    return result


def select(constraints=None, column_list=None, limit=100, desc=False, user_name=DEFAULTID, secure_key=None):
    """
    Call the select() web service to query the database and return a list of rows satisfying the constraints.

    Constraints are passed as a nested heirarchy of tuples or lists, each defining an operator and its argument/s.
    Each list consists of:
        -An operator string, currently one of '=', '<', '<=', '>', '>=', '!=', 'and', 'or', 'not' or 'like'
        -An argument, which could be a string value, a numeric value, a column name, OR another constraint tuple.
        -Another argument, which could be a string value, a numeric value, a column name, OR another constraint tuple.

    In the case of a unary operator, the list has two elements - the operator and one argument. Currently, the only
    unary operator is 'not'.

    For example, this constraint:
        ('or',
            ('and',
                ('>', 'obsid', 500),
                ('<', 'obsid', 1000)),
            ('not',
                ('like', 'projectid', '%000%')))

    Would translate to SQL looking like:
        WHERE (((obsid > 500) AND (obsid < 1000)) OR (NOT (projectid LIKE '%000%')))

    The function returns a dictionary contains any error messages, and the results of the call.
    It has the following key/value pairs:

    result['errors'] - A dictionary, containing integer keys, with values being any error messages (in order)
                       generated when processing that call.
    result['success'] - A Boolean, true for success or False if the call failed.
    result['query'] - The actual SQL query sent to the PostgreSQL server.
    result['rows'] - A list of rows satisfying the constraints, where each row is a list of values.

    :param constraints: A nested list of constraints, in the format described above.
    :param column_list: A list of column names to return in the SELECT query.
    :param limit: The maximum number of rows to return.
    :param desc: Boolean - if False, sort the rows by obsid, if True, sort the rows in reverse order of obsid.
    :param user_name: A project ID code (or a pseudo-ID), which the server ignores for SELECT queries.
    :param secure_key: A password, which the server ignores for SELECT queries.
    :return: The result dictionary, described above.
    """

    params = {"constraints": json.dumps(constraints),
              "column_list": json.dumps(column_list),
              "limit": limit,
              "user_name": user_name,
              "secure_key": secure_key}

    if desc:
        params["desc"] = 1   # Sort in descending order

    result = getmeta(servicetype="quality", service="select", params=params)
    return result
