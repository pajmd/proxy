import socket
import sys
from collections import deque
from select import select
import util.config_util as cu


tasks = deque()
recv_pending = {}
send_pending = {}


def format_pending_socket(pending):
    what = ''
    for k, v in pending.iteritems():
        what += '({}, {}) '.format(k.fileno(), v.__name__)
    return what


def run():
    while any([tasks, recv_pending, send_pending]):
        if not tasks:
            print("recv pending {} send pending {}".
                  format(format_pending_socket(recv_pending), format_pending_socket(send_pending)))
            ready_to_rcv, ready_to_send, xx = select(recv_pending, send_pending, [])
            for s in ready_to_rcv:
                tasks.append(recv_pending.pop(s))
            for s in ready_to_send:
                tasks.append(send_pending.pop(s))
        task = tasks.popleft()
        try:
            print('Running: {}'.format(task.__name__))
            operation, sock = next(task)
            print('next op: {} on: {} task: {}'.format(operation, sock.fileno(), task.__name__))
            if operation == 'recv':
                recv_pending[sock] = task
            elif operation == 'send':
                send_pending[sock] = task
            else:
                raise(RuntimeError('God knows'))
        except StopIteration:
            print('{} done'.format(task.__name__))


def listner(address, remote_host_name, remote_host_port):
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('Binding {}'.format(address))
    sock.bind(address)
    print('Listens to: {}'.format(sock.fileno()))
    sock.listen(5)
    while True:
        print('Yields {}'.format(sock.fileno()))
        yield 'recv', sock
        client, addr = sock.accept()
        print('Connected to {}'.format(addr))
        tasks.append(connect_to_remote_handler(client, remote_host_name, remote_host_port))


def client_to_remote_handler(client, remote_sock):
    while True:
        print('Waiting to receieve from client: {}'.format(client.fileno()))
        yield 'recv', client
        data = client.recv(1024)
        if data:
            print("received from client: {}".format(data))
            # yield when we know it will block
            yield 'send', remote_sock
            print('Sending to remote: {}'.format(data))
            remote_sock.send(data)
        else:
            print('Client Connection closed - closing remote connection')
            recv_pending.pop(remote_sock)
            client.close()
            remote_sock.close()
            break


def remote_to_client_handler(client, remote_sock):
    while True:
        yield 'recv', remote_sock
        data = remote_sock.recv(1024)
        if data:
            print("received from remote: {}".format(data))
            # yield when we know it will block
            yield 'send', client
            print('Sending to client: {}'.format(data))
            client.send(data)
        else:
            print('Remote Connection closed - closing client connection')
            recv_pending.pop(client)
            client.close()
            remote_sock.close()
            break


def connect_to_remote_handler(client, remote_host_name, remote_host_port):
    remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        remote_sock.connect((remote_host_name, remote_host_port))
        yield 'send', remote_sock
        tasks.append(client_to_remote_handler(client, remote_sock))
        tasks.append(remote_to_client_handler(client, remote_sock))
    except socket.error as er:
        client.close()
        print("Error connecting to remote- {} - closing client".format(er))


def main(configs):
    for config in configs:
        port = config['proxy']['proxy_port']
        remote_host_port = config['proxy']['port']
        remote_host_name = config['proxy']['host']
        tasks.append(listner(('', port), remote_host_name, remote_host_port))
    run()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        configs = cu.get_config(__file__)
        main(configs)
    elif 1 < len(sys.argv) < 4:
        print('Missing parameters\nusage: {} <port_num> <remote_host_name> <remote_host_port>'.format(sys.argv[0]))
        exit(1)
    else:
        try:
            config = {
                'proxy' : {
                    'proxy_port' : int(sys.argv[1]),
                    'host': sys.argv[2],
                    'port': int(sys.argv[3])
                }
            }
            configs = [config]
            main(configs)
        except ValueError as ex:
            print('Wrong port number\nusage: {} <port_num> <remote_host_name> <remote_host_port>'.format(sys.argv[0]))
            exit(1)
