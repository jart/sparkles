# http://packages.python.org/distribute/setuptools.html
# http://diveintopython3.org/packaging.html
# http://wiki.python.org/moin/CheeseShopTutorial
# http://pypi.python.org/pypi?:action=list_classifiers

from ez_setup import use_setuptools
use_setuptools(version="0.6c11")

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

version = __import__("sparkles").__version__

setup(
    name                 = "sparkles",
    version              = version,
    description          = "sparkles",
    long_description     = read("README.rst"),
    author               = "Justine Tunney",
    author_email         = "jtunney@lobstertech.com",
    license              = "GNU AGPL v3 or later",
    install_requires     = ["Django", "south", "django-gravatar", 'redis',
                            "python-memcached", "django-debug-toolbar"],
    packages             = find_packages(),
    include_package_data = True,
    zip_safe             = False,
    scripts              = ["scripts/" + f for f in os.listdir("scripts")
                            if not f.startswith(".")],
)
