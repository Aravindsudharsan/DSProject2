import socket
import json
import time
from threading import Thread 
from thread import start_new_thread
from random import randint
from random import random
import sys
import select

delay=10
array_client=[]
BUFFER_SIZE = 2000
socket_name_dict={}

class DistributedSnapshot:
    money = 1000
    local_state=0
    process_id = 0
    name = ""
    snapshot_id=0
    channels_state={}
    seen_snapshot_ids=[]
    record_channel_flag={}
    snapshot_marker_tracker={}


    def transfer_money(self,connection):
        amount = randint(0, 50)
        probability = random()
        #print "Probability value is ", probability
        if probability <= 0.2:
            connection.send(json.dumps(
                {
                    "amount":amount,
                    "type":"TRANSFER"
                }
                ))
            print self.name,  "sending $$", str(amount) , " to ", socket_name_dict[connection]
            self.money -= amount
            print "Current balance ", self.money



    def receive_money(self,data,connection):
        amount = data["amount"]
        self.money += amount
        print self.name, "receiving $$", str(amount), "from ", socket_name_dict[connection]
        print "Current balance " , self.money

    def snapshot_algorithm(self):

        self.snapshot_id = randint(0, 50)
        print "Initiating snapshot with snapshot id ",self.snapshot_id
        #saving local state
        self.local_state = self.money
        for client in array_client:
            client.send(json.dumps(
                {
                    'type':"MARKER",
                    'snapshot_id': self.snapshot_id
                }
                ))

dsObject = DistributedSnapshot()



def client_thread(ip,port,sendername,receivername):
    time.sleep(delay)
    toClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    toClient.connect((ip, port))
    array_client.append(toClient)
    socket_name_dict[toClient] = receivername
    data = json.dumps({'name': sendername, 'type': 'CON'})
    toClient.send(data)
    while 1:
        time.sleep(10)
        dsObject.transfer_money(toClient)

def send_marker_all_outgoing(conn):
    print "should write code for this"

def server_thread(conn):

    print "Connection established"
    stop_record={}
    while(1):
        data=conn.recv(2048)
        parsed_data = json.loads(data)

        if parsed_data['type'] == 'CON':
            socket_name_dict[conn]= parsed_data['name']
        elif parsed_data['type'] == 'TRANSFER':
            dsObject.receive_money(json.loads(data),conn)
            for k,v in dsObject.record_channel_flag.iteritems():
                if v == 1:
                    if k in stop_record and stop_record[k] == 1:
                        print "Not recording"
                    elif k in dsObject.channels_state:
                        dsObject.channels_state[k]+=[data]
                    else:
                        dsObject.channels_state[k] = [data]
        elif parsed_data['type'] == 'MARKER':
            print "Marker received from ", socket_name_dict[conn]
            received_snapshot_id=parsed_data['snapshot_id']
            if received_snapshot_id in dsObject.seen_snapshot_ids:
                #receiving marker from other input channels
                if dsObject.snapshot_marker_tracker[received_snapshot_id]:
                    if dsObject.snapshot_marker_tracker[received_snapshot_id] == 3: #3/2 --- CHECK
                        print "End of snapshot "
                    else:
                        stop_record[received_snapshot_id]=1
                        dsObject.snapshot_marker_tracker[received_snapshot_id]+=1;
                else:
                    dsObject.snapshot_marker_tracker[received_snapshot_id]=1
            else:
                #receiving marker for first time from initiator
                dsObject.seen_snapshot_ids.append(received_snapshot_id)
                # 1 here it should record its local state
                # 2 send markers on all outgoing channels
                dsObject.record_channel_flag[received_snapshot_id]=1


def get_input_from_user():

    input_stream = [sys.stdin]
    read_sockets, write_socket, error_socket = select.select(input_stream, [], [])

    while True:
        for input in read_sockets:
            message = sys.stdin.readline()
            if message == "snapshot\n":
                dsObject.snapshot_algorithm()


id = raw_input("Enter the process id :")
dsObject.process_id = id
with open("config.json", "r") as configFile:
    config = json.load(configFile)
    dsObject.name = config["client_details"][int(id)]["name"]

    for idx, val in enumerate(config["client_details"]):
        if idx != int(id):
            start_new_thread(client_thread,(val["ip"],int(val["port"]),dsObject.name,val["name"]))

tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpServer.bind((config["client_details"][int(id)]["ip"],int(config["client_details"][int(id)]["port"])))
tcpServer.listen(5)

start_new_thread(get_input_from_user,())

while True:
    conn, addr = tcpServer.accept()
    start_new_thread(server_thread,(conn,))






