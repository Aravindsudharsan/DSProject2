import socket
import json
import time
from threading import Thread 
from thread import start_new_thread
from random import randint
from random import random

delay=10
array_client=[]
BUFFER_SIZE = 2000
<<<<<<< HEAD

class DistributedSnapshot:
    money = 1000
    snapshot_variable=[]

    def transfer_money(self,connection):
        amount = randint(0, 50)
        probability = random()
        print "Probability value is ", probability

        if probability <= 0.2:
            connection.send(json.dumps({"amount":amount}))
            print "Client 1 sending ", amount , "to client socket ", connection
            self.money -= amount
            print "Current balance ", self.money



    def receive_money(self,data):
        amount = data["amount"]
        self.money += amount
        print "Client 1 receiving " , amount
        print "Current balance " , self.money

    def snapshot_algorithm(self):
        x=raw_input("Do you want to take a snapshot? Enter Y or N:")
        if x == 'Y':
            self.snapshot_variable.append(self.money)
            print self.snapshot_variable
	
dsObject = DistributedSnapshot()
||||||| merged common ancestors
#data=[]
=======


class DistributedSnapshot:
    money = 1000

    def transfer_money(self,connection):
        amount = randint(0, 50)
        probability = random()
        print "Probability value is ", probability

        if probability <= 0.2:
            connection.send(json.dumps({"amount":amount}))
            print "Client 1 sending ", amount , "to client socket ", connection
            self.money -= amount
            print "Current balance ", self.money



    def receive_money(self,data):
        amount = data["amount"]
        self.money += amount
        print "Client 1 receiving " , amount
        print "Current balance " , self.money

dsObject = DistributedSnapshot()
>>>>>>> 8e558d7c395fd92d4c45d52f95fd6fc8e37e9e77

id1=raw_input("Enter the process id:")

def client_thread(ip,port):
<<<<<<< HEAD
    tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    time.sleep(delay)
    tcpClient.connect((ip,port))
    array_client.append(tcpClient)
    print "[+] New server socket thread started for " + ip + ":" + str(port)
    #i=1
#for i in (1,5):
    while 1:
        time.sleep(10)
        dsObject.transfer_money(tcpClient)
||||||| merged common ancestors
	tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	time.sleep(delay)
	#if != config["client_details"][int(id1)]["port"]:	
	tcpClient.connect((ip,port))
	array_client.append(tcpClient)
	print "[+] New server socket thread started for " + ip + ":" + str(port)
	#MESSAGE="Hello"
	#tcpClient.send(MESSAGE)
	MESSAGE = raw_input("Enter message to send to server:/ Enter exit:")#added
	#while MESSAGE != 'exit':#added
	tcpClient.send(MESSAGE)#added
	data1 = tcpClient.recv(BUFFER_SIZE)#added
	print " Client received data:", data#added"""
=======

    tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    time.sleep(delay)

    tcpClient.connect((ip,port))
    array_client.append(tcpClient)
    print "[+] New server socket thread started for " + ip + ":" + str(port)

    i=1

    for i in (1,5):
        time.sleep(10)
        dsObject.transfer_money(tcpClient)

>>>>>>> 8e558d7c395fd92d4c45d52f95fd6fc8e37e9e77


def server_thread(conn):
    conn=conn[0]
    print "Connection established"
    data=conn.recv(2048)
    print "Server received data: ", data
    dsObject.receive_money(json.loads(data))

with open("config.json", "r") as configFile:
    config = json.load(configFile)
    print config
    for idx, val in enumerate(config["client_details"]):
<<<<<<< HEAD
        print val["ip"]
        print val["port"]
        if int(id1) != idx:
            print idx
            start_new_thread(client_thread,(val["ip"],int(val["port"])))
||||||| merged common ancestors
	print val["ip"]
	print val["port"]
	#print "next"
	if int(id1) != idx:
		#print "start"
		print idx
		start_new_thread(client_thread,(val["ip"],int(val["port"])))
=======
	print val["ip"]
	print val["port"]
	if int(id1) != idx:
		print idx
		start_new_thread(client_thread,(val["ip"],int(val["port"])))
>>>>>>> 8e558d7c395fd92d4c45d52f95fd6fc8e37e9e77


print config["client_details"][int(id1)]["ip"]
print config["client_details"][int(id1)]["port"]


#server part
tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
tcpServer.bind((config["client_details"][int(id1)]["ip"],int(config["client_details"][int(id1)]["port"]))) 

c=0
while True:
<<<<<<< HEAD
    tcpServer.listen(5)
    print "Waiting for connections from clients..."
    conn = tcpServer.accept()
    start_new_thread(server_thread,(conn,))
    c=c+1
    if c==1:
        start_new_thread(dsObject.snapshot_algorithm,())
||||||| merged common ancestors
	tcpServer.listen(5)
	print "Waiting for connections from clients..."
	conn = tcpServer.accept()
	start_new_thread(server_thread,(conn,))
	#print ip
	#print port
    	#newthread = ClientThread(ip,port) 
    	#newthread.start() 


=======
	tcpServer.listen(5)
	print "Waiting for connections from clients..."
	conn = tcpServer.accept()
	start_new_thread(server_thread,(conn,))


>>>>>>> 8e558d7c395fd92d4c45d52f95fd6fc8e37e9e77

