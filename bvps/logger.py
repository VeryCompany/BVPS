import logging


class actorLogFilter(logging.Filter):
    def filter(self, logrecord):
        return 'actorAddress' in logrecord.__dict__


class notActorLogFilter(logging.Filter):
    def filter(self, logrecord):
        return 'actorAddress' not in logrecord.__dict__


logcfg = {
    'version': 1,
    'formatters': {
        'normal': {
            'format': '%(asctime)s %(levelname)-8s %(message)s'
        },
        'actor': {
            'format': '%(asctime)s %(levelname)-8s %(actorAddress)s => %(message)s'
        }
    },
    'filters': {
        'isActorLog': {
            '()': actorLogFilter
        },
        'notActorLog': {
            '()': notActorLogFilter
        }
    },
    'handlers': {
        'h1': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'logs/bvps.log',
            # 'encoding':'utf-8',
            'formatter': 'normal',
            'filters': ['notActorLog'],
            'level': logging.INFO
        },
        'h2': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'logs/bvps_actor.log',
            # 'encoding':'utf-8',
            'formatter': 'actor',
            'filters': ['isActorLog'],
            'level': logging.DEBUG
        },
        'h3':{
            'class': 'logging.StreamHandler',
            'level': logging.INFO
        }
    },
    'loggers': {
        '': {
            'handlers': ['h1', 'h2'],
            'level': logging.INFO
        }
    }
}
