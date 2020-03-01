# 494P-Project
# Git cheat sheet
# https://rubygarage.org/blog/most-basic-git-commands-with-examples

TO DO:

Required:

	- RFC document
	- server process (not sure what this means)
	- client can send messages to a room (J Working on this)
	- client can send distinct message to multiple (selected) rooms (Might need clarification on this, is it per room or multiple at once)
	- server/client can gracefully handle client/server crashes (need to get clarification on this, may be done)
	- Programming style - I assume clean, readable with comments for functions/variables

Extra Credit:

	- private or ephermal messaging - can send based on username via command from client to server input
	- file transfer (I have no idea)
	- cloud connected server (I have no idea)
	- secure messaging - I assume this means it needs some cipher so that the server also can't read it -> receiving client needs key to decipher to read it
	  
Extra Stuff:

  - delete chat room (I was thinking only the creator can or if the owner leaves we can promote some other member - or we can let the creator leaving choose someone to promote)
    - decied how to handle when a client who is creator of a room disconnects (what we do with their chat room)
  - each room can have their own password or key to enter - needs list of admin users and users who are in the room (sub-user list per room)
  - on client side make output 'nicer'/cleaner/clearer
  - in clientthread, if there's a something like a switch case we could use instead of if/elif spam it would look much nicer
	  
Finished tasks:

  - client can leave a room 
  - client can join multiple (selected rooms)
  - client can list members of a room
  - client can join a room
  - client can connect to a server
  - client can create a room
  - client can list all rooms
  - client can list members of server
	- multiple clients can connect to a server
  - client can disconnect from a server
  - server can disconnect from clients
