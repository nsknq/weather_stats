import sys
import logging


def prepare_logging(logger_name, level=logging.DEBUG):
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logging_format = '%(levelname)s:%(name)s[LINE:%(lineno)d]: %(message)s'
    formatter = logging.Formatter(
        fmt=logging_format,
        datefmt='%m-%d %H:%M:%S')
    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
