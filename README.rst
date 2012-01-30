.. -*-rst-*-

==========
 sparkles
==========

:name:        sparkles
:description: sparkles
:copyright:   © 2012 Justine Tunney
:license:     GNU AGPL v3 or later


Usage
=====

Install from git into a virtualenv::

    sudo chmod go+rwt /opt  # let people create new files in /opt
    cd /opt
    virtualenv sparkles
    cd sparkles/sparkles
    source ../bin/activate
    git clone git://github.com/jart/sparkles.git
    cd sparkles
    make

How to run a debug server::

    make && sparkles-dev runserver

How to run a non-debug server::

    sudo apt-get install coffeescript lessc
    make pro && sparkles runserver
