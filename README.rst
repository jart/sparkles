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

Make sure you're on a debian/ubuntu system and then install these deps::

    sudo ./install-redis.sh 2.4.10
    sudo ./install-nodejs.sh 0.6.15
    sudo apt-get install -y python python-dev
    sudo npm install -g less coffee-script coffeelint uglify-js

Install from git into a virtualenv::

    sudo chmod go+rwt /opt  # let people create new files in /opt
    cd /opt
    virtualenv sparkles
    cd sparkles
    source bin/activate
    git clone git://github.com/jart/sparkles.git
    cd sparkles
    make

How to run a debug server::

    make && sparkles-dev runserver

How to run a non-debug server::

    make pro && sparkles runserver


Credits
=======

Big thanks go to Michael White for helping with the vision and planning of
this tool.
