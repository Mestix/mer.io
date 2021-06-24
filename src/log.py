import logging

import anticrlf

logger_settings = {
    'format': '%(asctime)s - %(name)-12s:%(lineno)d %(levelname)-8s %(message)s',
    'datetime': '%d-%m-%y %H:%M:%S',
    'level': 10
}


def get_logger(name):
    handler = logging.StreamHandler()
    formatter = anticrlf.LogFormatter(logger_settings['format'], datefmt=logger_settings['datetime'])
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
