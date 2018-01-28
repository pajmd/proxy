import socket
import logging
import time
import util.config_util as cu
from io import BlockingIOError
from .promise import Promise
from selectors2 import EVENT_READ, EVENT_WRITE


class Connector(object):
    def __init__(self, configs, selector):
        self.logger = logging.getLogger(cu.MAIN_LOG)
        for config in configs:
            self.proxy_port_num = config['proxy']['proxy_port']
            self.host_port = config['proxy']['port']
            self.host_name = config['proxy']['host']
            self.selector = selector

    def forward(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((socket.gethostname(), self.proxy_port_num))
        sock.setblocking(False)
        p = Promise()
        def on_accepted():
            p.set_result(None)
        self.selector.register(sock.fileno(), EVENT_READ, on_accepted)
        sock.listen(5)
        # while True:
        #     time.sleep(1)
        yield p
        self.selector.unregister(sock.fileno())
        self.logger.info('Accepted')
        (proxy_sock, address) = sock.accept()
        try:
            remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_sock.setblocking(False)
            try:
                remote_sock.connect((self.host_name, self.host_port))
            except Exception as er:  # BlockingIOError
                self.logger.exception(er)
                pass
            pc = Promise()

            def on_connected():
                pc.set_result(None)
            self.selector.register(remote_sock.fileno(), EVENT_WRITE, on_connected)
            yield pc
            self.selector.unregister(remote_sock.fileno())
            self.logger.info("connected")
            received_from_socket = None
            while True:
                pr = Promise()

                # should use lambda
                #on_readable_cl = lambda : readable(proxy_sock, remote_sock)
                def on_readable_client():
                    pr.set_result((proxy_sock.recv(1024), proxy_sock))

                def on_readable_remote():
                    pr.set_result((remote_sock.recv(1024), remote_sock))

                if received_from_socket:
                    if received_from_socket is proxy_sock:
                        self.selector.register(proxy_sock.fileno(), EVENT_READ, on_readable_client)
                    else:
                        self.selector.register(remote_sock.fileno(), EVENT_READ, on_readable_remote)
                else:
                    self.selector.register(proxy_sock.fileno(), EVENT_READ, on_readable_client)
                    self.selector.register(remote_sock.fileno(), EVENT_READ, on_readable_remote)
                chunk, received_from_socket = yield pr
#                self.selector.unregister(proxy_sock.fileno())
                self.selector.unregister(received_from_socket.fileno())
                sending_to_socket = remote_sock if received_from_socket is proxy_sock else proxy_sock
                if chunk:
                    self.logger.debug("read: {}".format(chunk))
                    # remote_sock.send(chunk)
                    sending_to_socket.send(chunk)
                else:
                    self.logger.warning("{} closed connection??".format(received_from_socket))
                    break
        except Exception as ex:
            self.logger.exception("God knows: {}".format(ex))
