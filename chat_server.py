import socket 
import select 
import sys 
from thread import *

"""The first argument AF_INET is the address domain of the 
socket. This is used when we have an Internet Domain with 
any two hosts The second argument is the type of socket. 
SOCK_STREAM means that data or characters are read in 
a continuous flow."""
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
  
# checks whether sufficient arguments have been provided 
#  if len(sys.argv) != 3: 
#      print "Correct usage: script, IP address, port number"
#      exit() 
  
# takes the first argument from command prompt as IP address 
IP_address = "0.0.0.0"
Port = 6677
#  IP_address = str(sys.argv[1]) 
#  Port = int(sys.argv[2]) 
# takes second argument from command prompt as port number 
  
""" binds the server to an entered IP address and at the 
specified port number. The client must be aware of these parameters """
server.bind((IP_address, Port)) 
  
""" listens for 100 active connections. This number can be 
increased as per convenience."""
server.listen(100) 

list_of_clients = [] 
addrs = []
usernames = []

#client.start(IP_address, Port)
  
def clientthread(conn, addr): 
    conn.send("Enter username: ")
    while True:
      username = conn.recv(2048)
      if username:
# can add a check to see if username is unique if we want
        username = username.strip('\n')
        if username not in usernames:
          try:
            usernames.append(username)
            break
          except:
            continue
        else:
          conn.send("Username already exists!\nEnter new username: ")

    print username + " has joined the room"
    # sends a message to the client whose user object is conn 
    conn.send("Welcome " + username + "!") 
    while True: 
            try: 
                message = conn.recv(2048) 
                if message: 
                    message = message.strip('\n')
                    """prints the message and address of the 
                    user who just sent the message on the server 
                    terminal"""
                    # disconnect user from server
                    if message == "/disconnect":
                      print "disconnecting user..."
                      remove(conn, addr, username)
                      #break;
                    # print list of users to specific user
                    elif message == "/users":
                      user_list = "Users:\n"
                      for each in range(len(usernames)):
                        user_list = user_list + usernames[each] + "\n"
                      user_list = user_list + "---------------"
                      conn.send(user_list)
                  # Calls broadcast function to send message to all 
                    else:
                      print "<" + username + "> " + message
                      message_to_send = "<" + username + "> " + message 
                      broadcast(message_to_send, conn, addr, username) 
                else: 
                  """message may have no content if the connection 
                  is broken, in this case we remove the connection"""
                  remove(conn) 
            except: 
              continue

"""Using the below function, we broadcast the message to all 
clients whose object is not the same as the one sending 
the message """
def broadcast(message, connection, addr, username): 
    for clients in list_of_clients: 
        if clients != connection: 
            try: 
                clients.send(message) 
            except: 
                clients.close() 
                # if the link is broken, we remove the client 
                remove(clients, addr, username) 
  
"""The following function simply removes the object 
from the list that was created at the beginning of  
the program"""
def remove(connection, addr, username): 
    if connection in list_of_clients: 
        list_of_clients.remove(connection) 
        addrs.remove(addr[0])
        usernames.remove(username)
        print username + " has disconnected"
        connection.send("You have been disconnected from the server\n")
        message_to_send = addr[0] + " has disconnected"
        broadcast(message_to_send, connection)
  
while True: 
    """Accepts a connection request and stores two parameters,  
    conn which is a socket object for that user, and addr  
    which contains the IP address of the client that just  
    connected"""
    conn, addr = server.accept() 
    """Maintains a list of clients for ease of broadcasting 
    a message to all available people in the chatroom"""
    list_of_clients.append(conn) 
    # prints the address of the user that just connected 
    addrs.append(addr[0])
    # creates and individual thread for every user  
    # that connects 
    start_new_thread(clientthread,(conn,addr))     
  
conn.close() 
server.close() 
