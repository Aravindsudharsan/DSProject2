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

id1=raw_input("Enter the process id:")

def client_thread(ip,port):
    tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    time.sleep(delay)
    tcpClient.connect((ip,port))
    array_client.append(tcpClient)
    print "[+] New server socket thread started for " + ip + ":" + str(port)
    while 1:
        time.sleep(10)
        dsObject.transfer_money(tcpClient)


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
        print val["ip"]
        print val["port"]
        if int(id1) != idx:
            print idx
            start_new_thread(client_thread,(val["ip"],int(val["port"])))


print config["client_details"][int(id1)]["ip"]
print config["client_details"][int(id1)]["port"]


#server part
tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
tcpServer.bind((config["client_details"][int(id1)]["ip"],int(config["client_details"][int(id1)]["port"]))) 

c=0
while True:
    tcpServer.listen(5)
    print "Waiting for connections from clients..."
    conn = tcpServer.accept()
    start_new_thread(server_thread,(conn,))
    c=c+1
    if c==1:
        start_new_thread(dsObject.snapshot_algorithm,())

