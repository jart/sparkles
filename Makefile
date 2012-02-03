dev:
	pip install sphinx pep8 pyflakes
	pip install -e .
	pep8     sparkles/admin.py
	pyflakes sparkles/admin.py
	pep8     sparkles/middleware.py
	pyflakes sparkles/middleware.py
	pep8     sparkles/models.py
	pyflakes sparkles/models.py
	pep8     sparkles/views.py
	pyflakes sparkles/views.py
	pep8     sparkles/tests.py
	pyflakes sparkles/tests.py
	pep8     sparkles/utils.py
	pyflakes sparkles/utils.py
	pep8     sparkles/api.py
	pyflakes sparkles/api.py
	pep8     sparkles/message.py
	pyflakes sparkles/message.py
	sparkles-dev syncdb
	sparkles-dev migrate
	sparkles-dev test sparkles
	make -C doc html

pro:
	pip install -e .
	lessc sparkles/static/sparkles/css/sparkles.less \
		sparkles/static/sparkles/css/sparkles.css
	lessc -x sparkles/static/sparkles/css/sparkles.less \
		sparkles/static/sparkles/css/sparkles.min.css
	coffee -o sparkles/static/sparkles/js \
		sparkles/static/sparkles/js/sparkles.coffee
	sparkles migrate
	sparkles collectstatic --noinput

deps:
	apt-get install -y python python-dev lessc coffeescript

newdb:
	rm -f sparkles.sqlite3
	make
	sparkles createsuperuser --username=jart --email=jtunney@lobstertech.com
