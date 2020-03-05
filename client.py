import socket 
import select 
import sys 
import os
  
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

#IP address of PSU
#IP_address = "127.0.0.50"
#IP_address = "0.0.0.0"
IP_address = "131.252.208.23"
#hostname = socket.gethostname()
#IP_address = socket.gethostbyname(hostname)
print IP_address
Port = 6677
server.connect((IP_address, Port)) 

while True: 
  try:
    # list of possible input streams 
    sockets_list = [sys.stdin, server] 
    read_sockets,write_socket, error_socket = select.select(sockets_list,[],[]) 
    
    for socks in read_sockets: 
      if socks == server: 
        message = socks.recv(2048) 
        if len(message) == 0:
          print "Connection to server lost!\n"
          server.close();
          exit();
        elif message == "You have been disconnected from the server":
          print message 
          exit();
        elif message[0:27] == "server-req-files-directory\n":
          numbered = False
          if message[27:] == "num":
            numbered = True
            num = 1
          file_list = [f for f in os.listdir('.') if os.path.isfile(f)]
          files = ""
          for f in file_list:
            if numbered:
              files += str(num) + ". "
              num += 1
            files += f + "\n"
          server.send(files)
        elif message[0:17] == "send-server-file\n":
          filename = message[17:]
          f = open(filename, 'rb')
          l = f.read(1024)
          while(l):
            server.send(l)
            l = f.read(1024)
          server.send("send-server-file\nend")
          f.close()
        elif message[0:20] == "receive-server-file\n":
          filename = message[20:]
          with open(filename, 'wb') as f:
            while True:
              try:
                data = socks.recv(1024)
                if len(data) == 0:
                  print "Connection to server lost!\n"
                  server.close();
                  exit();
                elif data.endswith("receive-server-file\nend"):
                  data.replace("receive-server-file\nend", "")
                  f.write(data)
                  f.close()
                  break
                else:
                  f.write(data)
              except:
                print "Connection to server lost!\n"
                server.close();
                exit()
              f.close()
        else:
          print message
      else: 
          message = sys.stdin.readline() 
          # send the message to the server
          server.send(message) 
          # written to only you
          sys.stdout.write("(You): ") 
          sys.stdout.write(message) 
          sys.stdout.flush() 
  except:
    print "\nDisconnected from server!"
    exit()

server.close() 
