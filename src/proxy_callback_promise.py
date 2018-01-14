import socket
import time
from selectors2 import DefaultSelector, EVENT_READ, EVENT_WRITE, _ERROR_TYPES

# see https://github.com/aosabook/500lines/blob/master/crawler/crawler.markdown

selector = DefaultSelector()

class Promise:
    def __init__(self):
        self.callback = None

    def resolve(self):
        self.callback()


def start_proxy(proxy_port, host, port):
    proxy_socket = socket(socket.AF_INET, socket.SOCK_STREAM)

    proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxy_socket.bind(socket.gethostname(), proxy_port)
    proxy_socket.setblocking(False)
    accept_callback = lambda : acceptable(proxy_socket, host, port)
    p = Promise()
    p.callback = accept_callback
    selector.register(proxy_socket, EVENT_READ, p)
    while 1:
        proxy_socket.listen(5)
        events = selector.select()
        for key, mask in events:
            promise = key.data
            promise.resolve()
        time.sleep(1)


def acceptable(proxy_socket, host, port):
    (client_socket, address) = proxy_socket.accept()
    establish_comm(client_socket, host, port)
    while 1:
        events = selector.select()
        for key, mask in events:
            promise = key.data
            promise.resolve()

def read_socket(sock_read, sock_write, buffer):
    selector.unregister(sock_read.fileno())
    bytes = sock_read.recv(1024)
    if bytes:
        sock_write.send(buffer)
        callback = lambda : read_socket(sock_read, sock_write, buffer)
        p = Promise()
        p.callback = callback
        selector.register(sock_read, EVENT_READ, p) # ??? no fileno

def establish_comm(client_socket, host, port):
    remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_sock.connect(host, port)
    remote_buffer = []
    remote_callbakc = lambda : read_socket(remote_sock, client_socket, remote_buffer)
    p = Promise()
    p.callback = remote_callbakc
    selector.register(remote_sock.fileno(), EVENT_READ, p)
    client_buffer = []
    client_callback = lambda : read_socket(client_socket, remote_sock, client_buffer)
    p2 = Promise()
    p2.callback = client_callback
    selector.register(client_socket.filena(), EVENT_READ, p2)



if __name__ == '__main__':
    proxy_port = 8555
    host_port = 2000
    host = "192.168.0.2"
    start_proxy(proxy_port, host, host_port)

