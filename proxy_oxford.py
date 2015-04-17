#!/usr/bin/python
# -*- coding: utf-8 -*-

"""The Oxford Mercury iPS power source for the magnets only accepts
1 connection.
ProxyOxford is a TCP proxy that joins any inbound connection to one
outbound connection to the iPS.

Based on http://voorloopnul.com/blog/\
a-python-proxy-in-less-than-100-lines-of-code/"""

import socket
import select
import time


DEBUG = False
TEST = False
BUFFER_SIZE = 4096
OXFORD_IPS = ('192.168.137.222', 7020)


class ProxyOxford:
    """ProxyOxford is a TCP proxy that joins any inbound connection to one
outbound connection to the iPS."""
    input_list = []

    def __init__(self, host='', port=7020, oxford_addr=OXFORD_IPS):
        """Arguments:
    'host': Host address, '' to accept all incoming connection.
    'port': Accept connection on this port, default to 7020.
    'oxford_addr': tuple for address and port of the Mercury iPS."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        self.sock.setblocking(False)
        self.sock.listen(5)
        self.input_list.append(self.sock)
        if TEST:
            self.oxford = ''
        else:
            self.oxford = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.oxford.bind(oxford_addr)

    def main_loop(self):
        "Wait the incoming connections and redirect them."
        while True:
            if DEBUG:
                print("Waiting for events...")
            readable, writable, excp = select.select(self.input_list, [], [])
            for _sock in readable:
                if _sock is self.sock:  # Incoming connection
                    self.on_accept(_sock)
                else:
                    data = _sock.recv(BUFFER_SIZE)
                    if data:  # Receive data
                        self.on_recv(_sock, data)
                    else:  # No data : Need to close connection
                        self.on_close(_sock)

    def on_accept(self, sock):
        "Create sockets for incoming connections."
        client_sock, client_addr = sock.accept()
        client_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client_sock.setblocking(False)
        if DEBUG:
            print("Accepted", client_sock, 'from', client_addr)
        self.input_list.append(client_sock)

    def on_close(self, conn):
        "Close socket when asked on the other side."
        if DEBUG:
            print("Closing", conn)

        self.input_list.remove(conn)
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()

    def on_recv(self, conn, data):
        """When data is received on incoming socket, send it to the Mercury iPS,
        wait for its response and send it back to the corresponding incoming
        socket"""
        if DEBUG:
            print("Received", repr(data), "from", conn)
        if TEST:
            response = data  # Echoing
        else:
            self.oxford.send(data)
            time.sleep(5e-3)
            response = self.oxford.recv(BUFFER_SIZE)
        if DEBUG:
            print("Get", repr(response), 'from Oxford')
        conn.send(response)

    def close(self):
        """Close every connections (inbounds and outbound)."""
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        if not TEST:
            self.oxford.shutdown(socket.SHUT_RDWR)
            self.oxford.close()


if __name__ == '__main__':
    proxy_oxford = ProxyOxford('', 7020)
    try:
        print("To quit ProxyOxford, press Ctrl+C.")
        proxy_oxford.main_loop()
    except KeyboardInterrupt:
        print("Close connections (ask by user).")
    finally:
        proxy_oxford.close()
