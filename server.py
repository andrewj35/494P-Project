import socket 
import select 
import sys 
import os
import re
import time
from thread import *

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
#IP_address = "0.0.0.0"
IP_address = "127.0.0.50"
# gets your IP address
#hostname = socket.gethostname()
#IP_address = socket.gethostbyname(hostname)
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
files = [f for f in os.listdir('.') if os.path.isfile(f)]
# list of commands : need to add new commands here so we can list them to make it easy for client
commands = ["/commands", "/disconnect", "/users", "/rooms", "/create", "/list", "/join", "/leave", "/upload", "/copy", "/message", "/ls", "/server", "/pm"]
# list of descriptions for what commands do
command_descriptions = ["List of commands.", 
"Disconnect from the server.",
"List of users in the server.",
"List of chatrooms.",
"Create a chatroom.",
"List users of a chatroom.",
"Join an existing chatroom.",
"Leave a chatroom you are a member of.",
"Upload file to the server.",
"Download file from server.",
"Message a specific chatroom you are a member of.",
"List files in your directory.",
"List files in the server's directory.",
"Privately messages someone."]
# list of users who are 'busy' so they shouldn't receive any messages
# mostly used for filetransfer - receiving message could mess with up/download
busy = []
# to close connection later
conn = None

def clientthread(conn, addr): 
# get a unique username to add to our list of users
  conn.send("Enter username: ")
  while True:
    username = get_message(conn, addr, "", "")
    try:
      username = re.sub(r"[\n\t]*", "",username)
      if username not in usernames and len(username) >= 2:
        try:
          usernames.append(username)
          break
        except:
          remove(conn, addr, "")
          break
      else:
        if len(username) < 3 and username not in usernames:
          conn.send("Username shold be 2 or more characters long!\nEnter new username: ")
        elif len(username) < 3:
          conn.send("Username shold be 2 or more characters long!\nEnter new username: ")
        elif username in usernames:
          conn.send("Username already exists!\nEnter new username: ")
        else:
          conn.send("Unknown error!")
          break
    except:
      if conn in list_of_clients:
        remove(conn, addr, "") 
      break

  print username + " joined the server"
# sends a message to this client
  conn.send("Welcome " + username + "!\nEnter /commands to see list of commands with their description.") 
  while True: 
    message = conn.recv(2048) 
    try: 
      if message and len(message) > 0:
        function_call(conn, addr, username, message)
      else: 
# message having no content means the user has disconnected
# also may handle client crashes
        if conn in conns and username in usernames:
          remove(conn, addr, username) 
        break
    except: 
# handles client connection lost (crash)
      if conn in list_of_clients and username in usernames:
        remove(conn, addr, username) 
      continue

def function_call(conn, addr, username, message):
  message = message.strip()
# print list of commands to client
  if message == commands[0]:
    command_list = "Commands:\n"
    for each in range(len(commands)):
      command_list = command_list + commands[each] + "\n - " + command_descriptions[each] + "\n"
    command_list = command_list + "---------------"
    conn.send(command_list)
# disconnect user from server
  elif message == commands[1]:
    print "disconnecting " + username + "..."
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
    conn.send(list_chatrooms(conn, addr, username, False))
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
    file_upload(conn, addr, username)
# allows user to download files uploaded to server
  elif message == commands[9]:
    copy_file(conn, addr, username)
# allows user to message a specific chat room
  elif message == commands[10]:
    broadcast_room(conn, addr, username)
# list files in your directory
  elif message == commands[11]:
    conn.send(list_my_files(conn, addr, username, False))
# list files in server directory
  elif message == commands[12]:
    conn.send(list_server_files(conn, addr, username, False))
# allows user to privately message someone
  elif message == commands[13]:
    private_message(conn, addr, username)
# sends message to whole server
  else:
    message_to_send = "" + username + ": " + message 
    print message_to_send
    broadcast(message_to_send, conn, addr, username) 

# gets user input and returns the string successfully received
# input header of "" if no header required 
def get_message(conn, addr, username, header):
  while True:
    message = conn.recv(2048)
    try:
      if message:
        message_to_send = header + message 
        return message_to_send
        break
      else:
        remove(conn, addr, username)
        break
    except:
      remove(conn, addr, username)
      continue

# send message to specific user
def private_message(conn, addr, username):
  try:
    conn.send("Enter username you wish to message: ")
    username = get_message(conn, addr, username, "")
    username = username.replace('\n', "")
    if username in usernames:
      conn.send("Enter message: ")
      header = "<Private Message> <Username: " + username + ">: "
      message_to_send = get_message(conn, addr, username, header)
      message_to_send = message_to_send.replace('\n', "")
      list_of_clients[(usernames.index(username))].send(message_to_send)
    else:
      conn.send("Username with that name doesn't exist!")
  except:
    conn.send("Error searching for username. Please ensure you are inputting a valid name.")

# returns list of chatrooms
def list_chatrooms(conn, addr, username, numbered):
  if numbered == True:
    num = 1;
  room_list = "List of Rooms:\n"
  for each in roomnames:
    if numbered == True:
      room_list = room_list + str(num) + ". "
      num += 1
    room_list = room_list + each.name + "\n"
  room_list = room_list + "---------------"
#  print "Printed list of chat rooms for " + username
  return room_list

# gets list of files in user's current directory
def list_my_files(conn, addr, username, numbered):
  if numbered == True:
    conn.send("server-req-files-directory\nnum")
  else:
    conn.send("server-req-files-directory\n")
  file_list = ("Files in your current directory:\n")
  while True:
    try:
      my_files = conn.recv(2048)
      if my_files:
        file_list += my_files
        file_list = file_list + "-------------"
        break
      else:
        remove(conn, addr, username)
        break
    except:
      remove(conn, addr, username)
      continue
  return file_list

# sends user list of files in the server
def list_server_files(conn, addr, username, numbered):
  file_list = ("Files in server directory:\n")
  if numbered == True:
    num = 1 
  for each in files:
    if numbered == True:
      file_list = file_list + str(num) + ". "
      num = num + 1
    file_list = file_list + each + "\n"
  file_list = file_list + "-------------"
  return file_list

# send message to specific chat room
def broadcast_room(conn, addr, username):
  rooms = list_chatrooms(conn, addr, username, True)
  conn.send(rooms+"\nEnter the corresponding number of the chat room you would like to message: ")
# TODO find out if this is good enough or if we need to do something like below (send to multiple rooms at once)
#  conn.send(rooms+"\nTo send a message to multiple rooms separate numbers by spaces (i.e. '1 2 4')\nEnter the corresponding number(s) of chat room(s) you would like to message: ")
  name = re.sub(r"[\n\t]*", "", get_message(conn, addr, username, ""))
  try:
    val = int(name)
    if val <= len(roomnames):
      if username in roomnames[val-1].users:
        conn.send("Enter message: ")
        header = "<Room: " + roomnames[val-1].name +"><Username: " + username + ">: " 
        message = get_message(conn, addr, username, header)
        message = message.replace('\n', "")
        for client in roomnames[val-1].conns:
          if client != conn:
            client.send(message)
      else:
        conn.send("You're not a member of that room so you can't send a message to it!")
    else:
      conn.send("Invalid input!")
  except:
    conn.send("Error!")

# copies file on the server into the user's current directory
def copy_file(conn, addr, username):
  message = ("WARNING! If a file of the same name you want to copy already exists in your directory it will be overwritten!")
  message += list_server_files(conn, addr, username, True)
  message += ("\nEnter the corresponding number of the file you would like to download: ")
  conn.send(message)
  name = get_message(conn, addr, username, "")
  try:
    val = int(name)
    if val <= len(files) and len(files) > 0 and val > 0:
      send_file(conn, addr, username, files[val-1])
      time.sleep(0.5)
      conn.send("File successfully copied!")
    else:
      conn.send("Invalid input!")
  except ValueError:
    conn.send("ValueError")
  except:
    conn.send("Error!")

# server sending file
def send_file(conn, addr, username, filename):
  busy.append(username)
  cmd = "receive-server-file\n"
  conn.send(cmd+filename)
  f = open(filename, 'rb')
  while True:
    l = f.read(1024)
    while(l):
      conn.send(l)
      l = f.read(1024)
    if not l:
      f.close()
      break
  conn.send(cmd + "end")
  print filename + " copied into " + username + "'s directory"
  busy.remove(username)

# gets file from clients directory to upload to server directory
def file_upload(conn, addr, username):
  my_files = list_my_files(conn, addr, username, True)
  conn.send(my_files + "\nEnter corresponding number of the file that you would like to upload: ")
  filename = get_message(conn, addr, username, "")
  file_list = my_files.split('\n')
  try:
    val = int(filename)
    if val < len(file_list)-1 and len(file_list) > 0 and val > 0:
      to_upload = file_list[val]
      to_upload = to_upload[3:]
      if to_upload in files:
        conn.send("A file with that name already exists! Cannot upload duplicate name files!")
        return
      get_file(conn, addr, username, to_upload)
      conn.send(to_upload + " successfully uploaded to server directory!")
      print(to_upload + " uploaded to server by " + username)
    else:
      conn.send("Invalid input!")
  except ValueError:
    conn.send("ValueError")
  except:
    conn.send("Error!")

# server receiving file from client
def get_file(conn, addr, username, filename):
  with open(filename, 'wb') as f:
    files.append(filename)
    conn.send("send-server-file\n" + filename)
    while True:
      try:
        message = conn.recv(2048)
        if message:
          if message == "send-server-file\nend":
            f.close()
            break
          f.write(message)      
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

# allows user to leave chat room if they are a member
def leave_room(conn, addr, username):
  obj = [x for x in roomnames if username in x.users]
  if len(obj) == 0:
    conn.send("You're not currently a members of any rooms!")
    return
  count = 1;
  my_rooms = "Rooms you are a member of:\n"
  for each in obj:
    my_rooms = my_rooms + str(count) + ". " + each.name + "\n"
    count = count + 1
  my_rooms = my_rooms +  "-------------"
  conn.send(my_rooms+"\nEnter corresponding number of chat room you want to leave: ")
  name = get_message(conn, addr, username, "")
  try:
    index = int(name)
    if index <= len(obj) and len(obj) > 0 and index > 0:
      index = index - 1
      obj[index].users.remove(username)
      obj[index].conns.remove(conn)
      conn.send("You have left chat room : " + obj[index].name)
      print username + " has left chat room " + obj[index].name
    else:
      conn.send("Invalid input!")
  except ValueError:
    conn.send("ValueError")
  except:
    conn.send("Error!")

# print list of users in a specific chat room
def print_room_users(conn, addr, username):
  rooms = list_chatrooms(conn, addr, username, True)
  conn.send(rooms+"\nEnter corresponding number of chat room: ")
  name = get_message(conn, addr, username, "")
  try:
    index = int(name)
    if index <= len(roomnames) and len(roomnames) > 0 and index > 0:
      index -= 1
      user_list = "Users:\n"
      for each in roomnames[index].users:
        user_list = user_list + each + "\n"
      user_list = user_list + "---------------"
#            print "printed client list for '" + name + "' chat room"
      conn.send(user_list)
    else:
      conn.send("Invalid input!")
  except ValueError:
    conn.send("ValueError")
  except:
    conn.send("Error!")

# try joining chat room if the chat room exists
def join_room(conn, addr, username):
  rooms = list_chatrooms(conn, addr, username, True)
  conn.send(rooms+"\nEnter the corresponding number of chat room to join: ")
  name = get_message(conn, addr, username, "")
  try:
    index = int(name)
    if index <= len(roomnames) and len(roomnames) > 0 and index > 0:
      index = index - 1
      if username not in roomnames[index].users:
        roomnames[index].users.append(username)
        roomnames[index].conns.append(conn)
#              print "added username " + username + " to room " + name
      else:
        conn.send("You are already a member of that chat room!")
    else:
      conn.send("Invalid input!")
  except ValueError:
    conn.send("ValueError")
  except:
    conn.send("Error!")

# create new chat room if one of the input name doesn't exist already
def create_room(conn, addr, username):
  rooms = "Note you cannot create a chatroom with same name as an existing chat room.\nExisting chat rooms:\n"
  rooms = rooms + list_chatrooms(conn, addr, username, False)
  conn.send(rooms+"\nEnter name of new chat room: ")
  while True:
    name = get_message(conn, addr, username, "")
    try:
      name = re.sub(r"[\n\t]*", "", name)
      if name not in roomnames:
        roomnames.append(chat_room(name, username, conn))
        print "chat room '" + name + "' has been created by " + username
        conn.send("Room has been created!")
        break
      else:
        conn.send("Chat room of that name already exists!\nPlease enter a different name: ")
    except ValueError:
      conn.send("ValueError")
      break
    except:
      conn.send("Error!")
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
# remove user from all rooms they were a part of
  rooms_in = [x for x in roomnames if username in x.users]
  for each in rooms_in:
    each.users.remove(username)
    each.conns.remove(conn)
  if connection in list_of_clients:
    list_of_clients.remove(connection) 
  if addr[0] in addrs: 
    addrs.remove(addr[0])
  if username in usernames: 
    usernames.remove(username)

# removes user from server
def remove(connection, addr, username): 
  remove_from_lists(connection, addr, username)
  connection.send("You have been disconnected from the server")
  print username + " has disconnected"
  
# actively listening for new clients who joining the server
while True:
  try: 
# grab the connection id and address of the client that just joined
    conn, addr = server.accept() 
# add client to list of clients
    list_of_clients.append(conn) 
# add client addr to list of addresses
    addrs.append(addr[0])
# creates and individual thread for every user  
    start_new_thread(clientthread,(conn,addr))     
  except:
    print "\nServer Crashed!"
    break

# if any connection was made
if conn != None:
  conn.close()
server.close()
