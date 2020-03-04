import socket 
import select 
import sys 
  
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

#IP address of PSU
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
