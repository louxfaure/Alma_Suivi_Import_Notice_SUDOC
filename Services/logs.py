import os
import logging
from logging.config import dictConfig
import colorlog
from logging.handlers import SMTPHandler

FORMAT = "%(asctime)s {app}  (%(module)s) [%(thread)d] %(levelname)-5s - %(message)s. [file=%(filename)s:%(lineno)d]"
DATE_FORMAT = None

def setup_logging(name, level="INFO", fmt=FORMAT, log_dir='/tmp'):
    formatted = fmt.format(app=name)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_colors = {
        'DEBUG': 'white',
        'INFO': 'green',
        'WARNING': 'yellow',  # Orange n'est pas supporté, jaune est la couleur la plus proche
        'ERROR': 'red',
        'CRITICAL': 'red',
    }

    logging_config = {
        "version": 1,
        'disable_existing_loggers': True,
        "formatters": {
            'standard': {
                'format': formatted
            },
            'brief': {
                'format': '%(asctime)s :: %(levelname)s :: %(message)s'
            },
            'colored': {
                '()': 'colorlog.ColoredFormatter',
                'format': "%(log_color)s" + formatted,
                'log_colors': log_colors
            }
        },
        "handlers": {
            'default': {
                'class': 'logging.StreamHandler',
                'formatter': 'colored',
                'level': level,
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'level': level,
                'formatter': 'standard',
                'filename': '{}/{}.log'.format(log_dir, name),
                'when': "d",
                'interval': 1,
                'backupCount': 5,
            },
            'mail': {
                'class': 'logging.handlers.SMTPHandler',
                'level': 'WARNING',
                'formatter': 'standard',
                'mailhost': (os.getenv('SMTP_SERVER_UB'), os.getenv('SMTP_PORT_UB')),  # Remplacez par les détails de votre serveur SMTP
                'fromaddr': os.getenv('ADMIN_MAIL_UB'),
                'toaddrs': [os.getenv('ADMIN_MAIL_UB')],  # Liste des destinataires
                'subject': '{} - Il y a un bug'.format(name),
                'credentials': (os.getenv('MAIL_LOGIN_UB'), os.getenv('MAIL_PWD_UB')),  # Remplacez par vos identifiants SMTP
                'secure': ()  # Utiliser STARTTLS
            }
        },
        "loggers": {
            name: {
                'handlers': ['default', 'file', 'mail'],
                'level': level
            }
        }
    }

    dictConfig(logging_config)
