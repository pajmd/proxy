import socket
import time
from selectors2 import DefaultSelector, EVENT_READ, EVENT_WRITE, _ERROR_TYPES
from config_util import get_config

selector = DefaultSelector()

def start_proxy(proxy_port, host, port):
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxy_socket.bind((socket.gethostname(), proxy_port))
    proxy_socket.setblocking(False)
    accept_callbakc = lambda : acceptable(proxy_socket, host, port)
    selector.register(proxy_socket, EVENT_READ, accept_callbakc)
    return proxy_socket


def event_loop(proxy_sockets):
    for proxy_socket in proxy_sockets:
        proxy_socket.listen(5)
    events = selector.select()
    while 1:
        for key, mask in events:
            callback = key.data
            callback()
        time.sleep(1)


def acceptable(proxy_socket, host, port):
    (client_socket, address) = proxy_socket.accept()
    establish_comm(client_socket, host, port)
    while 1:
        events = selector.select()
        for key, mask in events:
            callback = key.data
            callback()

def read_socket(sock_read, sock_write, buffer):
    selector.unregister(sock_read.fileno())
    buffer = sock_read.recv(1024)
    if bytes:
        sock_write.send(buffer)
        callback = lambda : read_socket(sock_read, sock_write, buffer)
        selector.register(sock_read.fileno(), EVENT_READ, callback) # ??? no fileno

def establish_comm(client_socket, host, port):
    remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_sock.connect((host, port))
    remote_buffer = []
    remote_callbakc = lambda : read_socket(remote_sock, client_socket, remote_buffer)
    selector.register(remote_sock.fileno(), EVENT_READ, remote_callbakc)
    client_buffer = []
    client_callback = lambda : read_socket(client_socket, remote_sock, client_buffer)
    selector.register(client_socket.fileno(), EVENT_READ, client_callback)



if __name__ == '__main__':
    proxy_port = 8555
    host_port = 2000
    host = "10.0.3.15"
    configs = get_config(__file__)
    sockets = []
    for config in configs:
        proxy_port_num = config['proxy']['proxy_port']
        host_port = config['proxy']['port']
        host_name = config['proxy']['host']
        sock = start_proxy(proxy_port_num, host_name, host_port)
        sockets.append(sock)
    event_loop(sockets)

