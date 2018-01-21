import os
import logging.handlers


def get_logger(me__file__):
    LOG_FILE = "{}.log".format(os.path.splitext(os.path.basename(me__file__))[0])
    MAX_SIZE_LOG = 1000000

    dir_log = "{}/../logs".format(os.path.dirname(me__file__))
    if not os.path.exists(dir_log):
        os.makedirs(dir_log)
    log_file = "{}/{}".format(dir_log, LOG_FILE)
    file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=MAX_SIZE_LOG, backupCount=2)
    logger = logging.getLogger(os.path.basename(os.path.splitext(os.path.basename(me__file__))[0]))
    logger.propagate = False
    log_formatter = logging.Formatter(
        '%(asctime)s - [%(filename)s:%(lineno)s - %(funcName)s() ] - [%(levelname)s] %(message)s')
    logger.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
    return logger
