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
	coffeelint sparkles/static/sparkles/js/*.coffee
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
		sparkles/static/sparkles/js/*.coffee
	uglifyjs -o sparkles/static/sparkles/js/sparkles.min.js \
		sparkles/static/sparkles/js/sparkles.js
	make -C sparkles/static/bootstrap bootstrap
	cp sparkles/static/bootstrap/bootstrap/js/bootstrap.min.js \
		sparkles/static/js
	sparkles migrate
	sparkles collectstatic --noinput

newdb:
	rm -f sparkles.sqlite3
	make
	sparkles createsuperuser --username=jart --email=jtunney@lobstertech.com
