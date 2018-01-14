import socket
import time
from selectors2 import DefaultSelector, EVENT_READ, EVENT_WRITE, ERROR_TYPES

selector = DefaultSelector()

def start_proxy(proxy_port, host, port):
    proxy_socket = socket(socket.AF_INET, socket.SOCK_STREAM)

    proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxy_socket.bind(socket.gethostname(), proxy_port)
    proxy_socket.setblocking(False)
    accept_callbakc = lambda : acceptable(proxy_socket, host, port)
    selector.register(proxy_socket, EVENT_READ, accept_callbakc)
    while 1:
        proxy_socket.listen(5)
        events = selector.select()
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
    bytes = sock_read.recv(1024)
    if bytes:
        sock_write.send(buffer)
        callback = lambda : read_socket(sock_read, sock_write, buffer)
        selector.register(sock_read, EVENT_READ, callback) # ??? no fileno

def establish_comm(client_socket, host, port):
    remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_sock.connect(host, port)
    remote_buffer = []
    remote_callbakc = lambda : read_socket(remote_sock, client_socket, remote_buffer)
    selector.register(remote_sock.fileno(), EVENT_READ, remote_buffer)
    client_buffer = []
    client_callback = lambda : read_socket(client_socket, remote_sock, client_buffer)
    selector.register(client_socket.filena(), EVENT_READ, client_callback)



if __name__ == '__main__':
    proxy_port = 8555
    host_port_port = 2000
    host = "192.168.0.2"
    start_proxy(proxy_port, host, host_port)

