import socket 
import select 
import sys 
  
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
IP_address = "0.0.0.0"
Port = 6677
server.connect((IP_address, Port)) 

while True: 
    # maintains a list of possible input streams 
    sockets_list = [sys.stdin, server] 
    """ There are two possible input situations. Either the 
    user wants to give  manual input to send to other people, 
    or the server is sending a message  to be printed on the 
    screen. Select returns from sockets_list, the stream that 
    is reader for input. So for example, if the server wants 
    to send a message, then the if condition will hold true 
    below.If the user wants to send a message, the else 
    condition will evaluate as true"""
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
              exit();
            print message 
        else: 
            message = sys.stdin.readline() 
            # send the message to the server
            server.send(message) 
            # written to only you
            sys.stdout.write("<You> ") 
            sys.stdout.write(message) 
            sys.stdout.flush() 

server.close() 
