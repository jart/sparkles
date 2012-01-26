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
    source bin/activate
    git clone REPO_URL
    easy_install pip
    pip install gunicorn
    pip install -e $(pwd)
    sparkles-dev syncdb
    sparkles-dev migrate

The ritual for running in development mode::

    sparkles-dev test sparkles
    sparkles-dev runserver

Generate the documentation::

    pip install sphinx
    make -C doc html
    firefox doc/_build/html/index.html


Production Mode
---------------

First you should update to the latest code::

    git pull
    pip install -e $(pwd)
    rm -f 
    sparkles migrate
    sparkles minify sparkles
    sparkles collectstatic --noinput
    sparkles compilemessages

Now install and configure nginx::

    sudo apt-get install nginx
    sudo ln -sf ../sites-available/sparkles.conf /etc/nginx/sites-enabled
    sudo /etc/init.d/nginx start

Start the backend gunicorn webserver::

    sudo cp conf/init.d/sparkles /etc/init.d
    sudo /etc/init.d/sparkles start

Now check it out by running firefox http://localhost/!!!

You can also run gunicorn manually::

    gunicorn_django --bind=127.0.0.1:7000 --workers=4 sparkles/settings.py

When using PostgreSQL, it is strongly recommended that you configure pgbouncer
on your system to significantly reduce request latency and memory consumption.
