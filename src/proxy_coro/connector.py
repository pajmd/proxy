import socket
import logging
import time
import util.config_util as cu
from io import BlockingIOError
from .promise import Promise
from selectors2 import DefaultSelector, EVENT_READ, EVENT_WRITE

selector = DefaultSelector()
logger = logging.getLogger("{}.{}".format(cu.MAIN_LOG, __name__))

class Connector(object):
    def __init__(self, configs):
        sockets = []
        for config in configs:
            self.proxy_port_num = config['proxy']['proxy_port']
            self.host_port = config['proxy']['port']
            self.host_name = config['proxy']['host']

    def forward(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((socket.gethostname(), self.proxy_port_num))
        sock.setblocking(False)
        p = Promise()
        def on_accepted():
            p.set_result(None)
        selector.register(sock, EVENT_READ, on_accepted)
        sock.listen(5)
        while True:
            time.sleep(1)
        yield p
        selector.unregister(sock.fileno())
        self.logger.info('Accepted')
        (proxy_sock, address) = sock.accept()
        try:
            remote_sock = socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_sock.setblocking(False)
            try:
                remote_sock.connect((self.host_name, self.host_port))
            except BlockingIOError as er:
                logger.info(er)
                pass
            pc = Promise()
            def on_connected():
                pc.set_result(None)
            selector.register(remote_sock.fileno(), EVENT_WRITE, on_connected)
            yield pc
            selector.unregister(remote_sock.fileno())
            logger.info("connected")


        except Exception as ex:
            logger.exception("God knows: {}".format(ex))


