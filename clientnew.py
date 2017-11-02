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

    def transfer_money(self,connection,id1,port):
        amount = randint(0, 50)
        probability = random()
        print "Probability value is ", probability
        if probability <= 0.2:
            connection.send(json.dumps({"amount":amount,"id":id1}))
            print "Client with id", str(id1),  " sending amount", str(amount) , "to client with socket ",str(port)
            self.money -= amount
            print "Current balance ", self.money



    def receive_money(self,data,id1):
        amount = data["amount"]
        id2=data["id"]
        self.money += amount
        print "Client with id" , str(id1), "received amount",str(amount),"from",str(id2)
        print "Current balance " , self.money

    def snapshot_algorithm(self):
        while True:
            x=raw_input("Do you want to take a snapshot? Enter Y or N:")
            if x == 'Y':
                self.snapshot_variable.append(self.money)
                print self.snapshot_variable

dsObject = DistributedSnapshot()

id1=raw_input("Enter the process id:")

def client_thread(ip,port,id1):
    tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    time.sleep(delay)
    tcpClient.connect((ip,port))
    array_client.append(tcpClient)
    print "[+] New server socket thread started for " + ip + ":" + str(port)
    while 1:
        time.sleep(10)
        dsObject.transfer_money(tcpClient,id1,port)


def server_thread(conn,id1):
    conn=conn[0]
    print "Connection established"
    data=conn.recv(2048)
    print "Server received data: ", data
    dsObject.receive_money(json.loads(data),id1)

with open("config.json", "r") as configFile:
    config = json.load(configFile)
    print config
    for idx, val in enumerate(config["client_details"]):
        print val["ip"]
        print val["port"]
        print idx
        start_new_thread(client_thread,(val["ip"],int(val["port"]),int(id1)))


print config["client_details"][int(id1)]["ip"]
print config["client_details"][int(id1)]["port"]


tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
tcpServer.bind((config["client_details"][int(id1)]["ip"],int(config["client_details"][int(id1)]["port"])))
c=0
while True:
    tcpServer.listen(5)
    print "Waiting for connections from clients..."
    conn = tcpServer.accept()
    start_new_thread(server_thread,(conn,int(id1)))
    c=c+1
    if c==1:
        start_new_thread(dsObject.snapshot_algorithm,())

