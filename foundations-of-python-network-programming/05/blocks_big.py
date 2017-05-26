#!/usr/bin/env python
# Foundations of Python Network Programming - Chapter 5 - blocks.py
# Sending data one block at a time.

# If you need to install numpy on a Rspberry Pi / SoCkit, do this:
# sudo apt-get install python-numpy

import socket, struct, sys, time
import numpy as np
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST = sys.argv.pop() if len(sys.argv) == 3 else '127.0.0.1'
PORT = 1060
struct_obj = struct.Struct('!I')  # for messages up to 2**32 - 1 in length

def recvall(sock, length):
    data = ''
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more:
            raise EOFError('socket closed %d bytes into a %d-byte message'
                           % (len(data), length))
        data += more
    return data

def get(sock):
    lendata = recvall(sock, struct_obj.size) # Would there be any harm in hard coding lendata to 4?? (portability, etc.)

    (length,) = struct_obj.unpack(lendata)
    return recvall(sock, length)

def put(sock, message):
    sock.send(struct_obj.pack(len(message)) + message)

if sys.argv[1:] == ['server']:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', PORT)) # Use '' for server to open up to the outside world (network)
    s.listen(1)
    print 'Listening at', s.getsockname()
    sc, sockname = s.accept()
    print 'Accepted connection from', sockname
    sc.shutdown(socket.SHUT_WR)
    while True:
        message = get(sc)
        if not message:
            break
        #print 'Message says:', repr(message)
        print 'testing numpy array stuff'
        ndata = np.frombuffer(message)
        print 'size of data: ' + str(len(message))
        print ndata[:8]
    sc.close()
    s.close()

elif sys.argv[1:] == ['client']:
    s.connect((HOST, PORT))
    s.shutdown(socket.SHUT_RD)
    #put(s, 'Beautiful is better than ugly.')
    #s.send(struct_obj.pack(len('Beautiful is better than ugly.')) + 'Beautiful is better than ugly.')
    #put(s, 'Explicit is better than implicit.')
    a = np.random.normal(1.0, 1.0, 1048576)
    data = bytearray(a)
    start_time = time.time();
    print 'length of message: ' + str(len(data))
    s.send(struct_obj.pack(len(data)) + data)
    #put(s, 'Simple is better than complex.')
    put(s, '')
    s.close()
    xfer_time = time.time() - start_time
    print("transfer time: " + str(xfer_time) + " Seconds...")

else:
    print >>sys.stderr, 'usage: streamer.py server|client [host]'
