import os
import site

VENV_DIR = os.path.expanduser('~/.virtualenvs/dsvbrowser')

site.addsitedir(VENV_DIR + '/lib/python2.7/site-packages')
activate_this = VENV_DIR + '/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from dsvbrowser import create_app
application = create_app()
