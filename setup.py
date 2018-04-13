import os
import re
import glob
import codecs as c
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
with c.open(glob.glob("%s/mwaqa/__init__.py" % here)[0]) as f:
    contents = f.read()
    version_number = re.search(r"__version__ = \"(\S+)\"", contents).group(1)

with c.open(glob.glob("%s/README.rst" % here)[0], encoding="utf-8") as f:
    long_description = f.read()

setup(name="mwaqa",
      version=version_number,
      description="Scripts and utilities to interface with the MWA quality assurance (QA) database.",
      long_description=long_description,
      url="https://github.com/MWATelescope/mwaqa",
      author="Christopher Jordan",
      author_email="christopher.jordan@curtin.edu.au",
      license="GPLv3",
      keywords="",
      packages=["mwaqa"],
      scripts=["scripts/mwaqa_query.py"],
      install_requires=["numpy",
                        "astropy",
                        "future"],
     )
