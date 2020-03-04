import socket 
import select 
import sys 
import os
from shutil import copyfile
from thread import *

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
#IP_address = "0.0.0.0"
IP_address = "127.0.0.50"
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
# list of files in directory => grab all files, other than the base server/client/README files in the server at startup
files = [f for f in os.listdir('.') if os.path.isfile(f) and f != "server.py" and f != "client.py" and f != "README.md"]
# list of commands : need to add new commands here so we can list them to make it easy for client
commands = ["/commands", "/disconnect", "/users", "/rooms", "/create", "/list", "/join", "/leave", "/upload_file", "/sync_files"]
# list of descriptions for what commands do
command_descriptions = ["List of commands.", 
"Disconnect from the server.",
"List of users in the server.",
"List of chatrooms.",
"Input name of chatroom they want to create, if it doesn\'t already exist, creates new chatroom with that name.",
"Input name of chatroom they want to list users of, if it exists, prints list of users in that chatroom.",
"Input name of chatroom they want to join, if it exists, they are added to the user list.",
"Input name of chatroom they want to leave, if it exists and they are a member, removes them from the chatroom.",
"Input name of file to upload it to the server.",
"Copies all files in the server to your directory"]
# list of users who are 'busy' so they shouldn't receive any messages
busy = []

def clientthread(conn, addr): 
# get a unique username to add to our list of users
  conn.send("Enter username: ")
  while True:
    try:
      username = conn.recv(2048)
      if username:
# gets rid of whitespace for unique names
        username = username.strip()
        if username not in usernames:
          try:
            usernames.append(username)
            break
          except:
            continue
# if user tried to create duplicate username
        else:
          conn.send("Username already exists!\nEnter new username: ")
      else:
        remove(conn, addr, "")
    except:
      continue

  print username + " joined the server"
# sends a message to this client
  conn.send("Welcome " + username + "!\nEnter /commands to see list of commands with their description.") 
  while True: 
    try: 
      message = conn.recv(2048) 
      if message: 
# gets rid of the '\n' char at end of message
        message = message.strip()
        if message == commands[0]:
          command_list = "Commands:\n"
          for each in range(len(commands)):
            command_list = command_list + commands[each] + "\n - " + command_descriptions[each] + "\n"
          command_list = command_list + "---------------"
          conn.send(command_list)
# disconnect user from server
        elif message == commands[1]:
          print "disconnecting user..."
          remove(conn, addr, username)
# print list of users 
        elif message == commands[2]:
          user_list = "Users:\n"
          for each in range(len(usernames)):
            user_list = user_list + usernames[each] + "\n"
          user_list = user_list + "---------------"
          conn.send(user_list)
# print the list of chat room
        elif message == commands[3]:
          print "Printing list of chat rooms for " + username
          room_list = "List of Rooms:\n"
          for each in roomnames:
            room_list = room_list + each.name + "\n"
          room_list = room_list + "---------------"
          conn.send(room_list)
# allows the user to create a new chat room
        elif message == commands[4]:
          create_room(conn, addr, username)
# allows user to list members of a chat room
        elif message == commands[5]:
          print_room_users(conn, addr, username)
# allows user to join a chat room
        elif message == commands[6]:
          join_room(conn, addr, username)
# allows user to leave a chat room if they're a member of input name
        elif message == commands[7]:
          leave_room(conn, addr, username)
# allows user to upload a file to the server
        elif message == commands[8]:
          update_files(conn, addr, username)
#          file_upload(conn, addr, username)
# sends message to whole server
        else:
# maybe output header for room message was sent from
# i.e.      message_to_send = "<" + chatroom_name + "> " + ... 
          message_to_send = "" + username + ": " + message 
          print message_to_send
          broadcast(message_to_send, conn, addr, username) 
      else: 
# message having no content means the user has disconnected
# also may handle client crashes
#        print "client thread else remove"
        remove(conn, addr, username) 
        break
    except: 
# handles client connection lost (crash)
#      print "client thread except remove"
      remove_from_lists(conn, addr, username) 
      continue

#TODO create function that removes user from all rooms they are a part of if they disconnect from server
# special case if they're owner of a room - have to decide how we handle that case
# def leave_all(conn, addr, username):

# TODO send message to specific chat room
#def broadcast_room(conn, username, room):

# copies all files on the server into the user's current directory
def update_files(conn, addr, username):
  conn.send("server-file-sync\n")
  while True:
    try:
      my_files = conn.recv(2048)
      if my_files:
        to_upload = [x for x in files if x not in my_files]
        for each in to_upload:
          send_file(conn, addr, username, each)
      else:
        remove(conn, addr, username)
        break
    except:
      remove(conn, addr, username)
      continue

def get_file(conn, addr, username, filename):
  with open(filename, 'wb') as f:
    files.append(filename)
    conn.send("send-server-file\n")
    conn.send(filename)
    while True:
      try:
        message = conn.recv(2048)
        if message:
          f.write(message)      
        else:
          f.close()
          break # upload done
      except:
        remove(conn, addr, username)
        continue

def send_file(conn, addr, username, filename):
  busy.append(username)
  f = open(filename, 'rb')
  l = f.read(1024)
  while(l):
    conn.send(l)
    l = f.read(1024)
  f.close()
  busy.remove(username)

def file_upload(conn, addr, username):
  conn.send("Enter filename (in the same folder) that you would like to upload: ")
  while True:
    try:
      message = conn.recv(2048)
      if message:
        filename,user = message.split(' ', 1)
        if filename:
# no duplicate files so we don't overwrite anything
          if filename not in files:
            get_file(conn, addr, username, filename)
            print(filename + " uploaded to server")
          else:
            conn.send("File with that name already exists!")
            break;
        else:
          conn.send("Incorrect input!")
          break
      else:
        remove(conn, addr, username)
        break
    except:
     remove(conn, addr, username)
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

# TODO quick leave function for when user quits room
# should remove all traces
# allows user to leave chat room if they are a member
def leave_room(conn, addr, username):
  conn.send("Enter name of chat room: ")
  while True:
    try:
      name = conn.recv(2048)
      if name:
        name = name.strip()
        obj = [x for x in roomnames if x.name == name]
        if obj:
          if username in obj[0].users:
            obj[0].users.remove(username)
            obj[0].conns.remove(conn)
            conn.send("You have left chat room : " + name)
            print username + " has left chat room " + name
            if obj[0].creator == username and obj[0].conn == conn:
              print username + " wants to delete '" + name + "'"
# TODO delete room if the creator wants to leave the room OR come up with way to replace creator
          else:
            conn.send("No user with that name found in chat room: " + name)
          break # break out of while loop
        else:
#          print "leave_room else remove"
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
#        print "print_room_users else remove"
        remove(conn, addr, username)
        break
    except:
#      print "print_room_users except remove"
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
#        print "join_room else remove"
        remove(conn, addr, username)
        break
    except:
#      print "join_room except remove"
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

# message to be broadcast to all the users in the server
def broadcast(message, connection, addr, username): 
  for clients in list_of_clients: 
    if clients != connection and usernames[(list_of_clients.index(clients))] not in busy: 
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
# TODO remove user from all chat rooms they are a part of
      broadcast(message_to_send, connection)
    else:
      print connection + " has disconnected"
# don't need to announce someone that couldn't even type has left

# removes user from server
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
