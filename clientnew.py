import socket
import json
from threading import Thread 
from thread import start_new_thread


array_client=[]
array_client1=[]
def client_thread(ip,port):
	tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	for i in config["client_details"]: 
		tcpClient.connect((i["ip"],i["port"]))
		array_client.append(tcpClient)
		print "[+] New server socket thread started for " + i["ip"] + ":" + str(i["port"])
	

with open("config.json", "r") as configFile:
    config = json.load(configFile)
    print config
    for i in config["client_details"]:
	print i["ip"]
	print i["port"]
	print "next"
	#start_new_thread(client_thread,(i["ip"],i["port"]))


id1=raw_input("Enter the process id:")
print config["client_details"][int(id1)]["ip"]
print config["client_details"][int(id1)]["port"]

tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
tcpServer.bind((config["client_details"][int(id1)]["ip"],int(config["client_details"][int(id1)]["port"]))) 

tcpClient1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
for i in config["client_details"]: 
    tcpClient1.connect((i["ip"],int(i["port"])))
    array_client1.append(tcpClient1)

while True:
	tcpServer.listen(5) 
    	print "Waiting for connections from clients..." 
    	(conn, (ip,port)) = tcpServer.accept() 
	start_new_thread(client_thread,(ip,port))
	#print ip
	#print port
    	#newthread = ClientThread(ip,port) 
    	#newthread.start() 



	



	



	
