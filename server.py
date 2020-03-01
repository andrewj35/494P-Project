import socket 
import select 
import sys 
from thread import *

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
  
IP_address = "0.0.0.0"
Port = 6677
server.bind((IP_address, Port)) 
  
# listens for 100 active connections
server.listen(100) 
# list of connections of clients
list_of_clients = [] 
# list of IP addresses of clients
addrs = []
# list of usernames for clients
usernames = []
# list of rooms : contains name of room, conn and username of creator
roomnames = []
# list of commands : need to add new commands here so we can list them to make it easy for client
commands = ["/commands", "/disconnect", "/users", "/rooms", "/create", "/list", "/join", "/leave"]
# list of descriptions for what commands do
command_descriptions = ["List of commands.", 
"Disconnect from the server.",
"List of users in the server.",
"List of chatrooms.",
"Input name of chatroom they want to create, if it doesn\'t already exist, creates new chatroom with that name.",
"Input name of chatroom they want to list users of, if it exists, prints list of users in that chatroom.",
"Input name of chatroom they want to join, if it exists, they are added to the user list.",
"Input name of chatroom they want to leave, if it exists and they are a member, removes them from the chatroom."]

def clientthread(conn, addr): 
# loop in which we will get a unique username to add to our list of users
    conn.send("Enter username: ")
    while True:
      try:
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
        else:
          remove(conn, addr, "")
      except:
        continue

    print username + " joined the server"
    # sends a message to the client whose user object is conn 
    conn.send("Welcome " + username + "!\nEnter /commands to see list of commands with their description.") 
    while True: 
      try: 
        message = conn.recv(2048) 
        if message: 
# gets rid of the '\n' char at end of message
          message = message.strip()
          if message == "/commands":
            command_list = "Commands:\n"
            for each in range(len(commands)):
              command_list = command_list + commands[each] + "\n - " + command_descriptions[each] + "\n"
              command_list = command_list + "---------------"
            conn.send(command_list)
# disconnect user from server
          elif message == "/disconnect":
            print "disconnecting user..."
            remove(conn, addr, username)
          # print list of users to specific user
          elif message == "/users":
            user_list = "Users:\n"
            for each in range(len(usernames)):
              user_list = user_list + usernames[each] + "\n"
            user_list = user_list + "---------------"
            conn.send(user_list)
# print the list of chat room
          elif message == "/rooms":
            print "Printing list of chat rooms for " + username
            room_list = "List of Rooms:\n"
            for each in roomnames:
              room_list = room_list + each.name + "\n"
            room_list = room_list + "---------------"
            conn.send(room_list)
# allows the user to create a new chat room
          elif message == "/create":
            create_room(conn, addr, username)
# allows user to list members of a chat room
          elif message == "/list":
            print_room_users(conn, addr, username)
# allows user to join a chat room
          elif message == "/join":
            join_room(conn, addr, username)
# allows user to leave a chat room if they're a member of input name
          elif message == "/leave":
            leave_room(conn, addr, username)
# Calls broadcast function to send message to all 
          else:
# maybe output header for room message was sent from
# i.e.      message_to_send = "<" + chatroom_name + "> " + ... 
            message_to_send = "" + username + ": " + message 
            print message_to_send
            broadcast(message_to_send, conn, addr, username) 
        else: 
# message having no content means the user has disconnected
# also may handle client crashes
          print "client thread else remove"
          remove(conn, addr, username) 
          break
      except: 
# handles client connection lost (crash)
        print "client thread except remove"
        remove_from_lists(conn, addr, username) 
        continue

class chat_room:
  def __init__(self, name, creator, conn):
    self.name = name
    self.creator = creator
    self.conn = conn
    self.users = []
    self.conns = []
    self.users.append(creator) # add creator to user list
    self.conns.append(conn) # add creator conn to conns list

#TODO create function that removes user from all rooms they are a part of if they disconnect from server
# special case if they're owner of a room - have to decide how we handle that case
# def leave_all(conn, addr, username):

# allows user to leave chat room if they are a member
def leave_room(conn, addr, username):
  conn.send("Enter name of chat room: ")
  while True:
    try:
      name = conn.recv(2048)
      if name:
        name = name.strip()
        if any(x.name == name for x in roomnames):
          for each in roomnames:
            if each.name == name:
              if username in each.users and conn in each.conns:
                each.users.remove(username)
                each.conns.remove(conn)
                conn.send("You have left chat room : " + name)
                print username + "has left chat room " + name
                if each.creator == username and each.conn == conn:
                  print username + " wants to delete '" + name + "'"
# TODO delete room if the creator wants to leave the room OR come up with way to replace creator
              else:
                conn.send("No user with that name found in chat room: " + name)
            break # break out of for loop
          break # break out of while loop
        else:
          print "leave_room else remove"
          conn.send("Chat room with that name wasn't found!")
          break
      else:
        print "leave_room else remove"
        remove(conn, addr, username)
        break
    except:
      print "print_room_users except remove"
      remove(conn, addr, username)
      continue

# print list of users in a specific chat room
def print_room_users(conn, addr, username):
  conn.send("Enter name of chat room: ")
  while True:
    try:
      name = conn.recv(2048)
      if name:
        name = name.strip()
        obj = [x for x in roomnames if x.name == name]
        if obj:
          user_list = "Users:\n"
          for user in obj[0].users:
            user_list = user_list + user + "\n"
          user_list = user_list + "---------------"
          print "printed client list for '" + name + "' chat room"
          conn.send(user_list)
        else:
          conn.send("Chat room with that name wasn't found!")
        break # break out of while loop
      else:
        print "print_room_users else remove"
        remove(conn, addr, username)
        break
    except:
      print "print_room_users except remove"
      remove(conn, addr, username)
      continue

# try joining chat room if the chat room exists
def join_room(conn, addr, username):
  conn.send("Enter name of chat room to join: ")
  while True:
    try:
      name = conn.recv(2048)
      if name:
        name = name.strip()
        obj = [x for x in roomnames if x.name == name]
        if obj:
          if username not in obj[0].users and conn not in obj[0].conns:
            obj[0].users.append(username)
            obj[0].conns.append(conn)
            print "added " + username + " to " + name
          else:
            conn.send("You are already a member of that chat room!")
        else:
          conn.send("Chat room with that name doesn't exist!")
        break # break out of while loop
      else:
        print "join_room else remove"
        remove(conn, addr, username)
        break
    except:
      print "join_room except remove"
      remove(conn, addr, username)
      continue

# create new chat room if one of the input name doesn't exist already
def create_room(conn, addr, username):
  conn.send("Enter name of new chat room: ")
  while True:
    try:
      name = conn.recv(2048)
      if name:
        name = name.strip()
        if any(x.name == name for x in roomnames):
          conn.send("Chat room of that name already exists!\nPlease enter a different name: ")
        else:
          roomnames.append(chat_room(name,username,conn))
          print "chat room '" + name + "' has been created by " + username
          conn.send("Room has been created!")
          break
      else:
# make sure we can handle client crashes 
        remove(conn, addr, username) 
    except:
      remove(conn, addr, username) 
      continue

# TODO send message to specific chat room
#def broadcast_room(conn, username, room):

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
  
# removes user from all the lists - connection has been lost
def remove_from_lists(connection, addr, username):
  if connection in list_of_clients:
    list_of_clients.remove(connection) 
    if addr[0] in addrs: addrs.remove(addr[0])
    if username in usernames: 
      usernames.remove(username)
      print username + " has disconnected"
      message_to_send = username + " has disconnected"
      broadcast(message_to_send, connection)
    else:
      print connection + " has disconnected"
# don't need to announce someone that couldn't even type has left

# removes user from server - based on connection, addr, and username
def remove(connection, addr, username): 
  if connection in list_of_clients: 
    connection.send("You have been disconnected from the server\n")
    remove_from_lists(connection, addr, username)
  
# actively listening for new clients who joining the server
while True: 
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
