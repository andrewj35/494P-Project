# 494P-Project
# Git cheat sheet
# https://rubygarage.org/blog/most-basic-git-commands-with-examples

TO DO:

Extra Credit = EC
Required = R
R	- RFC document
R	- server process (not sure what this means)
R	X- client can join a room
R	- client can leave a room
R	X- client can list members of a room
R	- client can send messages to a room
R	- client can send distinct message to multiple (selected) rooms
R	- client can join multiple (selected rooms) => headers for each room i.e. <room_name>
R	- server/client can gracefully handle client/server crashes (need to get clarification on this)
R	- Programming style - I assume clean, readable with comments for functions/variables

EC	- private or ephermal messaging - can send based on username via command from client->server input
EC	- file transfer (I have no idea)
EC	- cloud connected server (I have no idea)
EC	- secure messaging - I assume this means it needs some cipher so that the server
	  also can't read it -> receiving client needs key to decipher to read it
	  
Extra?	- each room can have their own password or key to enter - needs list of admin users
	  and users who are in the room (sub-user list per room)
	  
Finished tasks
	- client can connect to a server
	- client can create a room
	- client can list all rooms
	- client can list members of server (not room yet)
	- multiple clients can connect to a server
	- client can disconnect from a server
	- server can disconnect from clients
