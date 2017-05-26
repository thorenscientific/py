print "Hello, world! From Socket server"
# Echo client program
import socket

HOST = '192.168.1.126'    # The remote host
PORT = 1973              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send('Hello, world... Holy Smokes it freakin worked!!!')
data = s.recv(1024)
s.close()
print 'Received', repr(data)
