import logging


logger_settings = {
    'format': '%(asctime)s - %(name)-12s %(levelname)-8s %(message)s',
    'datetime': '%d-%m-%y %H:%M:%S',
    'level': 10
}


def get_logger(name):
    logging.basicConfig(format=logger_settings['format'], datefmt=logger_settings['datetime'])

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger


