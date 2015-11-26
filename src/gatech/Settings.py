

LOG_SETTINGS = {
    'version':1,
    'disable_existing_loggers':False,
    'formatters':{
        'verbose':{
            'format':'%(levelname)s %(asctime)s %(thread)d %(message)s'
        },
    },
    'handlers':{
        'console':{
            'class':'logging.StreamHandler',
            'formatter':'verbose',
        }
    },
    'loggers':{
        'gatech':{
            'handlers':['console'],
            'level':'DEBUG',
            'propagate':False,
        },
        'minient':{
            'handlers':['console'],
            'level':'INFO',
            'propagate':False,
        }
    }


}