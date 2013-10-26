from flask import Flask

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py', silent=True)

if not app.debug and not app.testing:
    import logging
    import os

    from logging.handlers import RotatingFileHandler, SMTPHandler

    app.logger.setLevel(logging.INFO)

    log_path = os.path.join(app.instance_path, 'info.log')
    file_handler = RotatingFileHandler(log_path,
                                       maxBytes=100000, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'))

    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    try:
        mail_handler = SMTPHandler(app.config['MAIL_SERVER'],
                                   app.config['MAIL_FROM'],
                                   app.config['ADMINS'],
                                   'Error on %s' % app.config['SERVER_NAME'],
                                   (app.config['MAIL_USERNAME'],
                                    app.config['MAIL_PASSWORD']),
                                   ())
        mail_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
    except KeyError:
        pass


from . import models
from . import views
