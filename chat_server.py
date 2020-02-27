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
  
IP_address = "0.0.0.0"
Port = 6677
  
""" binds the server to an entered IP address and at the 
specified port number. The client must be aware of these parameters """
server.bind((IP_address, Port)) 
  
""" listens for 100 active connections. This number can be 
increased as per convenience."""
server.listen(100) 

list_of_clients = [] 
addrs = []
usernames = []
# TODO decide how we're going ot handle chat room/users in chat rooms
#dictionary of roomnames
#roomnames = {}
#dictionary of rooms
rooms = {}

def clientthread(conn, addr): 
# loop in which we will get a unique username to add to our list of users
    conn.send("Enter username: ")
    while True:
      username = conn.recv(2048)
      if username:
# gets rid of whitespace for clearer unique names
        username = username.strip()
        if username not in usernames:
          try:
            usernames.append(username)
            break
          except:
            continue
# when someone is trying to create duplicate username
        else:
          conn.send("Username already exists!\nEnter new username: ")

    print username + " has joined the room"
    # sends a message to the client whose user object is conn 
    conn.send("Welcome " + username + "!") 
    while True: 
            try: 
                message = conn.recv(2048) 
                if message: 
                    # gets rid of the '\n' char at end of message
                    message = message.strip('\n')
                    # disconnect user from server
                    if message == "/disconnect":
                      print "disconnecting user..."
                      remove(conn, addr, username)
                    # print list of users to specific user
                    elif message == "/users":
                      user_list = "Users:\n"
                      for each in range(len(usernames)):
                        user_list = user_list + usernames[each] + "\n"
                      user_list = user_list + "---------------"
                      conn.send(user_list)
# TODO create system of chat rooms that can be created -> associated with
# names via dictionary (roomnames) and another dictionary (rooms) that contains
# objects of users, anything else we might need
                    elif message == "/rooms":
# TODO create list of chat rooms created, this will print the list
                    elif message == "/create_room":
# TODO create function to create new chat room
# user should automatically join and be an 'admin' such that they can destory the room
                    elif message == "/leave":
# TODO create leave room function like below - if an admin leaves a room it should destory
# the room and kick all users that were in the chat room
#                     leave_room(conn, addr, username)
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

# message to be broadcast to all the users in the server
def broadcast(message, connection, addr, username): 
    for clients in list_of_clients: 
        if clients != connection: 
            try: 
                clients.send(message) 
            except: 
                clients.close() 
                # if the link is broken, we remove the client 
                remove(clients, addr, username) 
  
# removes user from server - based on connection, addr, and username
def remove(connection, addr, username): 
    if connection in list_of_clients: 
        list_of_clients.remove(connection) 
        addrs.remove(addr[0])
        usernames.remove(username)
        print username + " has disconnected"
        connection.send("You have been disconnected from the server\n")
        message_to_send = addr[0] + " has disconnected"
        broadcast(message_to_send, connection)
  
# actively listening for new clients who joining the server
while True: 
    """Accepts a connection request and stores two parameters,  
    conn which is a socket object for that user, and addr  
    which contains the IP address of the client that just  
    connected"""
# grab the connection id and address of the client that just joined
    conn, addr = server.accept() 
# add client to list of clients
    list_of_clients.append(conn) 
# add client addr to list of addresses
    addrs.append(addr[0])
    # creates and individual thread for every user  
    # that connects 
    start_new_thread(clientthread,(conn,addr))     
  
# close connection to server for client
conn.close() 
server.close() 
