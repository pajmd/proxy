import socket
import sys
from collections import deque
from select import  select



tasks = deque()
recv_pending = {}
send_pending = {}


def run():
    while any([tasks, recv_pending, send_pending]):
        print("recv pending {} send pending {}".format(recv_pending, send_pending))
        ready_to_rcv, ready_to_send, xx = select(recv_pending, send_pending, [])
        for s in ready_to_rcv:
            tasks.append(recv_pending.pop(s))
        for s in ready_to_send:
            tasks.append(send_pending.pop(s))
    task = tasks.popleft()
    try:
        operation, sock = next(task)
        if operation == 'recv':
            recv_pending[sock] = task
        elif operation == 'send':
            send_pending[sock] = task
        else:
            raise(RuntimeError('God knows'))
    except StopIteration:
        print('{} done'.format(task))


def listner(address):
    sock =socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(address)
    print('Listens')
    sock.listen(5)
    while True:
        print('Yields')
        yield 'recv', sock
        client, addr = sock.accept()
        print('Connected to {}'.format(addr))
        tasks.append(handler(client))


def listner_sync(address):
    sock =socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(address)
    print('Listens')
    sock.listen(5)
    while True:
        client, addr = sock.accept()
        print('Connected to {}'.format(addr))
        handler(client)


def handler(client):
    while True:
        yield 'recv', client
        data = client.recv(1024)
        if data:
            print(data)
            # yield when we know it will block
            yield 'send', client
            client.send("echoing: {}".format(data))
        else:
            print('Connection closed')
            client.close()
            break


def handler_sync(client):
    while True:
        data = client.recv(1024)
        if data:
            print(data)
            client.send("echoing: {}".format(data))
        else:
            print('Connection closed')
            client.close()
            break


def main(port):
    listner(('', port))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: {} <port_num>'.format(sys.argv[0]))
        exit(1)
    try:
        portnum = int(sys.argv[1])
    except Exception:
        print('usage: {} <port_num>'.format(sys.argv[0]))
        exit(1)
    min(portnum)


