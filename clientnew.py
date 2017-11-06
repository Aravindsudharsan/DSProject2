import socket
import json
import time
from threading import Thread
from thread import start_new_thread
from random import randint
from random import random
import sys
import select
import re

delay = 10
array_client = []
BUFFER_SIZE = 2000
socket_name_dict = {}


class DistributedSnapshot:
    money = 1000
    local_state = 0
    process_id = 0
    name = ""
    snapshot_id = 0
    channels_state = {}
    seen_snapshot_ids = []
    record_channel_flag = {}
    snapshot_marker_tracker = {}

    def transfer_money(self, connection):
        amount = randint(0, 50)
        probability = random()
        # print "Probability value is ", probability
        if probability <= 0.2:
            #time.sleep(10)
            connection.send(json.dumps({"amount": amount, "type": "TRANSFER"}))
            print self.name, "sending $$", str(amount), " to ", socket_name_dict[connection]
            self.money -= amount
            print "Current balance ", self.money

    def receive_money(self, data, connection):
        amount = data["amount"]
        self.money += amount
        print self.name, "receiving $$", str(amount), "from ", socket_name_dict[connection]
        print "Current balance ", self.money

    def snapshot_algorithm(self):

        self.snapshot_id = randint(0, 50)
        print "Initiating snapshot with snapshot id ", self.snapshot_id
        # saving local state
        self.local_state = self.money
        self.seen_snapshot_ids.append(self.snapshot_id)
        print "CHECKING SEEN SNAPSHOT IDS", self.seen_snapshot_ids
        for client in array_client:
            #time.sleep(25)
            #print "Sending marker in ALGORITHM TO ", client, "with snapshot id ", self.snapshot_id
            client.send(json.dumps({'type': "MARKER", 'snapshot_id': self.snapshot_id}))

    def local_state_process(self,received_snapshot_id):
        self.local_state = self.money
        print "local saved state is", self.local_state
        for client in array_client:
            #time.sleep(25)
            #print "Sending marker AFTER SAVING LOCAL STATE TO ", client, "with snapshot id ", received_snapshot_id
            client.send(json.dumps({'type': "MARKER", 'snapshot_id': received_snapshot_id}))


dsObject = DistributedSnapshot()


def client_thread(ip, port, sendername, receivername):
    time.sleep(delay)
    toClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    toClient.connect((ip, port))
    array_client.append(toClient)
    socket_name_dict[toClient] = receivername
    data = json.dumps({'name': sendername, 'type': 'CON'})
    toClient.send(data)
    while 1:
        time.sleep(5)
        dsObject.transfer_money(toClient)


#def send_marker_all_outgoing(conn):
   # print "should write code for this"


def server_thread(conn):
    print "Connection established"
    stop_record = {}
    while (1):
        data = conn.recv(2048)
        data=re.split('(\{.*?\})(?= *\{)', data)
        #parsed_data = json.loads(data)
        #print data
        for message in data:
            if message == '\n':
                continue
            parsed_data = json.loads(message)
            if 'name' in parsed_data:
                print "checking for message", message, " from ",parsed_data['name']
        #print parsed_data
            if parsed_data['type'] == 'CON':
                socket_name_dict[conn] = parsed_data['name']
            elif parsed_data['type'] == 'TRANSFER':
                dsObject.receive_money(json.loads(message), conn)
                for k, v in dsObject.record_channel_flag.iteritems():
                    if v == 1:
                        if k in stop_record and stop_record[k] == 1:
                            print "Have stopped recording "
                        elif k in dsObject.channels_state:
                            dsObject.channels_state[k] += [message]
                            print "Adding intermediate channel state to list of channel states "
                            print dsObject.channels_state
                        else:
                            dsObject.channels_state[k] = [message]
                            print "Adding first channel state to list of channel states ",dsObject.channels_state
            elif parsed_data['type'] == 'MARKER':
                time.sleep(10)
                print "Marker received from ", socket_name_dict[conn]
                print 'Connection object is ***', conn
                received_snapshot_id = parsed_data['snapshot_id']
                if received_snapshot_id in dsObject.seen_snapshot_ids:
                    print "Received snapshot id is in seen snapshot ids"
        # receiving marker from other input channels
                    if received_snapshot_id in dsObject.snapshot_marker_tracker:
        #3/2 --- CHECK
                        print "Value of snapshot marker tracker ", dsObject.snapshot_marker_tracker[received_snapshot_id]

                        if dsObject.snapshot_marker_tracker[received_snapshot_id] == 2:
                            print "End of snapshot",received_snapshot_id
                            print "local state of the process is",dsObject.local_state
                            print " channel state of the process is",dsObject.channels_state

                        else:
                            print "Marker received from intermediate channel -- stopping recording for this channel",socket_name_dict[conn]
                            stop_record[received_snapshot_id] = 1
                            dsObject.snapshot_marker_tracker[received_snapshot_id] += 1
                    else:
                        dsObject.snapshot_marker_tracker[received_snapshot_id] = 1
                else:
        # receiving marker for first time from initiator
                    print "Received snapshot id is NOT in seen snapshot ids, SEEING FOR FIRST TIME"
                    dsObject.seen_snapshot_ids.append(received_snapshot_id)
                    dsObject.snapshot_marker_tracker[received_snapshot_id] = 1
        #  record its local state
                    dsObject.local_state_process(received_snapshot_id)
        # 2 send markers on all outgoing channels
                    dsObject.record_channel_flag[received_snapshot_id] = 1


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
            start_new_thread(client_thread, (val["ip"], int(val["port"]), dsObject.name, val["name"]))

tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpServer.bind((config["client_details"][int(id)]["ip"], int(config["client_details"][int(id)]["port"])))
tcpServer.listen(5)

start_new_thread(get_input_from_user, ())

while True:
    conn, addr = tcpServer.accept()
    start_new_thread(server_thread, (conn,))
