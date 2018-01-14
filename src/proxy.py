import socket
import os
import select
import logging.handlers
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    import json
    YAML_AVAILABLE = False
import time

LOG_FILE = "{}.log".format(os.path.splitext(os.path.basename(__file__))[0])
MAX_SIZE_LOG = 100000


def start_proxy(proxy_port, host, port):
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.info('Starting proxy on {}:{}'.format(socket.gethostname(), proxy_port))
    proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        proxy_socket.bind((socket.gethostname(), proxy_port))
        proxy_socket.listen(5)
        while 1:
            (client_socket, address) = proxy_socket.accept()
            logger.info("proxy {}:{} accepted connection".format(socket.gethostname(), proxy_port))
            pid = os.fork()
            if pid == -1:
                logger.info('Error forking')
            if pid == 0:
                logger.info("Child proxy {} establsing connections".format(client_socket.getpeername()))
                proxy_socket.close()
                establish_comm(client_socket, host, port)
                # being a child we _exit
                os._exit(0)
            else:
                logger.info("parent listener {}:{} keep listening".format(socket.gethostname(), proxy_port))
                client_socket.close()
    except Exception as ex:
        logger.exception("Error start proxy manager proxy port: {} remote {}:{} - {}"
                         .format(proxy_port, host, port, ex))
        raise


def establish_comm(client_socket, host, port):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        logger.info("proxy from {} to {}:{} connecting".format(client_socket.getpeername(), host, port))
        remote_socket.connect((host, port))
        logger.info("proxy from {} to {}:{} started".format(client_socket.getpeername(), host, port))
        inputs = [client_socket, remote_socket]
        while inputs:
            readable, writable, priority = select.select(inputs, [], inputs)
            for s in readable:
                byte_buffer = s.recv(1024)
                if byte_buffer:
                    if s is client_socket:
                        logger.info("received from {} sending to {}".
                                    format(client_socket.getpeername(), remote_socket.getpeername()))
                        remote_socket.send(byte_buffer)
                    else:
                        logger.info("received from {} sending to {}".
                                    format(remote_socket.getpeername(), client_socket.getpeername()))
                        client_socket.send(byte_buffer)
                else:
                    logger.info("remote socket closed connection: {}".format(remote_socket.getpeername()))
                    remote_socket.close()
                    client_socket.close()
                    return
    except Exception as ex:
        logger.exception("error while proxy establishng connection with remote: {}".format(ex))
        raise


if __name__ == '__main__':
    dir_log = "{}/../logs".format(os.path.dirname(__file__))
    if not os.path.exists(dir_log):
        os.makedirs(dir_log)
    log_file = "{}/{}".format(dir_log, LOG_FILE)
    file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=MAX_SIZE_LOG, backupCount=2)
    logger = logging.getLogger(os.path.basename(os.path.splitext(os.path.basename(__file__))[0]))
    logger.propagate = False
    log_formatter = logging.Formatter(
        '%(asctime)s - [%(filename)s:%(lineno)s - %(funcName)s() ] - [%(levelname)s] %(message)s')
    logger.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)

    logger.info('stuff')
    logger.info("in {}".format(__file__))
    dir_file = "{}/../config".format(os.path.dirname(__file__))
    if YAML_AVAILABLE:
        config_file = "{}/proxy_config.yaml".format(dir_file)
        loader = yaml.load
    else:
        config_file = "{}/proxy_config.json".format(dir_file)
        loader = json.load
    with open(config_file, "r") as f:
        configs = loader(f)
    for config in configs:
        proxy_port_num = config['proxy']['proxy_port']
        host_port = config['proxy']['port']
        host_name = config['proxy']['host']
        logger.info("Sarting proxy listening to {} forwarding to {}:{}".format(proxy_port_num, host_name, host_port))
        pid_manager = os.fork()
        if pid_manager == -1:
            logger.error('Proxy mager error forking')
        if pid_manager == 0:
            logger.info("proxy manager child")
            start_proxy(proxy_port_num, host_name, host_port)
        else:
            logger.info("proxy manager getting to next proxy to start if any")
    while 1:
        time.sleep(30)
