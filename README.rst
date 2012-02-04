.. -*-rst-*-

==========
 sparkles
==========

:name:        sparkles
:description: sparkles
:copyright:   © 2012 Justine Alexandra Roberts Tunney
:license:     GNU AGPL v3 or later


Usage
=====

Install from git into a virtualenv.  Please note that you need Django 1.4 from
git because it hasn't been released yet::

    sudo chmod go+rwt /opt  # let people create new files in /opt
    cd /opt
    virtualenv sparkles
    cd sparkles
    source bin/activate
    git clone git://github.com/django/django.git
    pip install -e django
    git clone git://github.com/jart/sparkles.git
    cd sparkles
    make deps
    make

How to run a debug server::

    make && sparkles-dev runserver

How to run a non-debug server::

    make pro && sparkles runserver
