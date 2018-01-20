import socket
from util.log_util import get_logger
from util.config_util import get_config

class Connector(object):
    def __init__(self):
        logger = get_logger(__file__)
        configs = get_config(__file__)
        sockets = []
        for config in configs:
            self.proxy_port_num = config['proxy']['proxy_port']
            self.host_port = config['proxy']['port']
            self.host_name = config['proxy']['host']

    def forward(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((socket.gethostname(), self.proxy_port))
        sock.setblocking(False)
