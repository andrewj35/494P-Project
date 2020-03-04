import socket 
import select 
import sys 
import os
  
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

#IP_address = "0.0.0.0"
IP_address = "127.0.0.50"
Port = 6677
server.connect((IP_address, Port)) 

while True: 
    # list of possible input streams 
    sockets_list = [sys.stdin, server] 
    read_sockets,write_socket, error_socket = select.select(sockets_list,[],[]) 
  
    for socks in read_sockets: 
        # when user first joins room
        if socks == server: 
            message = socks.recv(2048) 
            if len(message) == 0:
              print "Connection to server lost!\n"
              server.close();
              exit();
            elif message == "You have been disconnected from the server\n":
              print message 
              exit();
            elif message == "server-file-sync\n":
              files = [f for f in os.listdir('.') if os.path.isfile(f) and f != "server.py" and f != "client.py" and f != "README.md"]
              server.send(message)
            elif message[0:16] == "send-server-file\n":
              filename = message[0:]
              f = open(filename, 'rb')
              l = f.read(1024)
              while(l):
                server.send(l)
                l = f.read(1024)
              f.close()
            else:
              print message 
        else: 
            message = sys.stdin.readline() 
            # send the message to the server
            server.send(message) 
            # written to only you
            sys.stdout.write("(You): ") 
            sys.stdout.write(message) 
            sys.stdout.flush() 

server.close() 
