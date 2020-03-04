# 494P-Project
Git cheat sheet: https://rubygarage.org/blog/most-basic-git-commands-with-examples

TO DO LIST:

Required:

	- RFC document
	- server process (not sure what this means)
	- server/client can gracefully handle client/server crashes (need to get clarification on this, may be done)
	- Programming style - I assume clean, readable with comments for functions/variables

Extra Credit:

	- private or ephermal messaging (maybe they can send based on username via command from client to server input)
	- file transfer (I have no idea)
	- cloud connected server (I have no idea)
	- secure messaging - I assume this means it needs some cipher so that the server also can't read it -> receiving client needs key to decipher to read it
	  
Extra Stuff:

  	- delete chat room (only creator should be able to do this)
    		- decide how to handle when a client, who is creator of a room, disconnects (what we do with their chat room - promote another member of the chat room if one exists or delete it anyways and send message to members that room was deleted)
  	- each room can have their own password or key to enter - needs list of admin users and users who are in the room (sub-user list per room)
  	- on client side make output 'nicer'/cleaner/clearer
  	- in clientthread, if there's a something like a switch case we could use instead of if/elif spam it would look much nicer
	  
Finished:

  	- client can leave a room 
  	- client can join multiple (selected rooms)
  	- client can list members of a room
  	- client can join a room
  	- client can connect to a server
  	- client can create a room
  	- client can list all rooms
  	- client can list members of server
  	- multiple clients can connect to server
  	- client can disconnect from a server
  	- server can disconnect from clients
	- client can send messages to a room (J Similar to a channel)
	- client can send distinct message to multiple (selected) rooms (Can specify which room to send to)
	- Programming style - I assume clean, readable with comments for functions/variables
