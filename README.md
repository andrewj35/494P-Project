# 494P-Project
# Git cheat sheet
# https://rubygarage.org/blog/most-basic-git-commands-with-examples

DO TO:

Extra Credit = EC
Required = R
Extra stuff = ES
R	- RFC document
R	- clients can list members of a room
R	- class of rooms from the main server based on name of chat room (unique?)
ES	- each room can have their own password or key to enter - needs list of admin users
	  and users who are in the room (sub-user list per room)
R	- commands to destroy the chat room, leave chat room, connect to chat room
R	- list of all rooms created (sorted by locked/open rooms - if we make private rooms)
	  (this may be its own class)
R	- client can join multiple (selected rooms) => headers for each room i.e. <room_name>
R	- check what she means by server/client can gracefully handle client/server crashes
EC	- private or ephermal messaging - can use chat room class or create its own; send
	  send based on username 
EC	- file transfer (I have no idea)
EC	- cloud connected server (I have no idea)
EC	- secure messaging - I assume this means it needs some cipher so that the server
	  also can't read it -> receiving client needs key to decipher to read it

Done
	- client can connect to a server
	- client can list members of server (not room yet)
	- multiple clients can connect to a server
	- client can disconnect from a server
	- server can disconnect from clients