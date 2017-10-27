import socket
import json
import time
from threading import Thread 
from thread import start_new_thread

delay=10
array_client=[]
#array_client1=[]
BUFFER_SIZE = 2000

id1=raw_input("Enter the process id:")
def client_thread(ip,port):
	tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	time.sleep(delay)
	#if != config["client_details"][int(id1)]["port"]:	
	tcpClient.connect((ip,port))
	array_client.append(tcpClient)
	print "[+] New server socket thread started for " + ip + ":" + str(port)
	MESSAGE = raw_input("Enter message to send to server:/ Enter exit:")#added
	while MESSAGE != 'exit':#added
		tcpClient.send(MESSAGE)#added
		#data = tcpClient.recv(BUFFER_SIZE)#added
		#print " Client received data:", data#added


def server_thread(conn):
	print "Connection established"
	def run(self):#added
		while True:#added
			data = conn.recv(2048)#added
			print "Server received data:", data#added
			#MESSAGE = raw_input("Enter response to send to client/Enter exit:")#added
			#if MESSAGE == 'exit':#added
			#	break#added
			#conn.send(MESSAGE)#added

with open("config.json", "r") as configFile:
    config = json.load(configFile)
    print config
    for idx, val in enumerate(config["client_details"]):
	print val["ip"]
	print val["port"]
	#print "next"
	if int(id1) != idx:
		#print "start"
		print idx
		start_new_thread(client_thread,(val["ip"],int(val["port"])))


#print "check"
print config["client_details"][int(id1)]["ip"]
print config["client_details"][int(id1)]["port"]


#server part
tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
tcpServer.bind((config["client_details"][int(id1)]["ip"],int(config["client_details"][int(id1)]["port"]))) 

while True:
	tcpServer.listen(5)
	print "Waiting for connections from clients..."
	conn = tcpServer.accept()
	start_new_thread(server_thread,(conn,))
	#print ip
	#print port
    	#newthread = ClientThread(ip,port) 
    	#newthread.start() 

#client as client

"""tcpClient1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
for i in config["client_details"]: 
    time.sleep(delay)    
    tcpClient1.connect((i["ip"],int(i["port"])))
    array_client1.append(tcpClient1)"""


	



	



	
