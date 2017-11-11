import socket
import json
import time
from threading import Thread
from thread import start_new_thread
from random import randint
from random import random
import threading
import sys
import select
import re
import Queue
import traceback

delay = 20
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
    send_queue=Queue.Queue()
    recv_channels = []

    def setup_receive_channels(self,s):
        while 1:
            try:
                conn, addr = s.accept()
            except:
                continue
            self.recv_channels.append(conn)
            print 'Connected with ' + addr[0] + ':' + str(addr[1])


    def transfer_money(self):
        while True:
            time.sleep(3)
            amount = 10
            client_id = randint(0,2)
            connection = array_client[client_id]
            probability = random()
            # print "Probability value is ", probability
            if probability <= 0.5:
                #connection.send(json.dumps({"amount": amount, "type": "TRANSFER"}))
                temp_dict = {}
                temp_dict[connection] = json.dumps({"amount": amount, "type": "TRANSFER"})
                self.send_queue.put(temp_dict)
                print self.name, "sending $$", str(amount), " to ", socket_name_dict[connection]
                self.money -= amount
                print "Current balance ", self.money
                print ""

    def receive_money(self, data, connection):
        amount = data["amount"]
        self.money += amount
        print self.name, "receiving $$", str(amount), "from ", socket_name_dict[connection]
        print "Current balance ", self.money
        print ""

    def snapshot_algorithm(self):

        self.snapshot_id = randint(0, 50)
        print "Initiating snapshot with snapshot id ", self.snapshot_id
        # saving local state
        self.local_state = self.money
        self.seen_snapshot_ids.append(self.snapshot_id)
        self.record_channel_flag[self.snapshot_id] = 1
        #print "CHECKING SEEN SNAPSHOT IDS", self.seen_snapshot_ids
        for client in array_client:
            print "Sending marker in ALGORITHM TO ", client, "with snapshot id ", self.snapshot_id
            #client.send(json.dumps({'type': "MARKER", 'snapshot_id': self.snapshot_id}))
            temp_dict = {}
            temp_dict[client] = json.dumps({'type': "MARKER", 'snapshot_id': self.snapshot_id})
            self.send_queue.put(temp_dict)

    def local_state_process(self,received_snapshot_id):
        self.local_state = self.money
        #print "local saved state is", self.local_state
        for client in array_client:
            print "Sending marker AFTER SAVING LOCAL STATE TO ", socket_name_dict[client], "with snapshot id ", received_snapshot_id
            #client.send(json.dumps({'type': "MARKER", 'snapshot_id': received_snapshot_id}))
            temp_dict = {}
            temp_dict[client] = json.dumps({'type': "MARKER", 'snapshot_id': received_snapshot_id})
            self.send_queue.put(temp_dict)

    def send_messages(self):
        while True:
            try:
                connection_message = self.send_queue.get(True, 0.05)
                for connection, message in connection_message.iteritems():
                    connection.send(message)
                    #print "CHECK CONNECTION ***", connection
                    #print "CHECK MESSAGE *** ", message
            except Queue.Empty:
                # print "in except block"
                continue



dsObject = DistributedSnapshot()


def client_thread():
    connected_array = []

    while True:

        # print config["client_details"]
        for idx, val in enumerate(config["client_details"]):
            if idx != int(id) and idx not in connected_array:
                # print idx
                # print connected_array
                ip = val["ip"]
                port = int(val["port"])
                sendername = dsObject.name
                receivername = val["name"]
                try:
                    toClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    toClient.connect((ip, port))
                except:
                    # print "tried connecting"
                    continue
                    time.sleep(3)
                connected_array.append(idx)
                array_client.append(toClient)
                socket_name_dict[toClient] = receivername
                data = json.dumps({'name': sendername, 'type': 'CON'})
                toClient.send(data)
                # dsObject.transfer_money(toClient)
        if len(connected_array) == 3:
            break


def receive_messages():
    #print "Connection established"
    stop_record = {}
    while (1):
        for conn in dsObject.recv_channels:
            data = conn.recv(2048)
            data=re.split('(\{.*?\})(?= *\{)', data)
            #parsed_data = json.loads(data)
            #print data
            for message in data:
                if not message:
                    continue
                if message == '\n':
                    continue
                #print "checking for message--",message,"CHECK"
                parsed_data = json.loads(message)
                #if 'name' in parsed_data:
                    #print "checking for message", message, " from ",parsed_data['name']
                #print parsed_data
                if parsed_data['type'] == 'CON':
                    socket_name_dict[conn] = parsed_data['name']
                elif parsed_data['type'] == 'TRANSFER':
                    dsObject.receive_money(parsed_data, conn)
                    parsed_data_channel = parsed_data
                    parsed_data_channel['from'] = socket_name_dict[conn]
                    for k, v in dsObject.record_channel_flag.iteritems():
                        if v == 1:
                            # print "Stop record ", stop_record
                            if k in stop_record:
                                print "Checking stop record and conn below --- ",stop_record[k]
                                if conn in stop_record[k]:
                                    print "Checking stop record's conn object  --- ", stop_record[k][conn]
                            if k in stop_record and conn in stop_record[k] and stop_record[k][conn]== 1:
                                print "Recording stopped for this channel "
                            elif k in dsObject.channels_state:
                                dsObject.channels_state[k] += [parsed_data_channel]
                                #print "Adding intermediate channel state to list of channel states "
                                #print dsObject.channels_state
                            else:
                                dsObject.channels_state[k] = [parsed_data_channel]
                                #print "Adding first channel state to list of channel states ",dsObject.channels_state
                elif parsed_data['type'] == 'MARKER':
                    print "Marker received from ", socket_name_dict[conn]

                    received_snapshot_id = parsed_data['snapshot_id']
                    if received_snapshot_id in dsObject.seen_snapshot_ids:
                        #print "Received snapshot id is in seen snapshot ids"
                        #print " snap shot marker value is",dsObject.snapshot_marker_tracker
                        # receiving marker from other input channels
                        if received_snapshot_id in dsObject.snapshot_marker_tracker:
                        #3/2 --- CHECK
                            #print "Value of snapshot marker tracker ", dsObject.snapshot_marker_tracker[received_snapshot_id]

                            if dsObject.snapshot_marker_tracker[received_snapshot_id] == 2:
                                print "---------------------------------------------------"
                                print "End of snapshot",received_snapshot_id
                                print "LOCAL STATE: ",dsObject.local_state
                                #print "checking for channel state",dsObject.channels_state
                                snapshot_channel_state=[]
                                if received_snapshot_id in dsObject.channels_state:
                                    snapshot_channel_state=dsObject.channels_state[received_snapshot_id]
                                    print "MONEY ON THE FLY "
                                    for channel_state in snapshot_channel_state:
                                        print dsObject.name, "receiving ", channel_state["amount"], " from ", channel_state['from']
                                else:
                                    print "MONEY ON THE FLY - NONE"
                                finalvalue_snapshot=0
                                for state in snapshot_channel_state:
                                    finalvalue_snapshot+=state['amount']
                                total_amount=dsObject.local_state+finalvalue_snapshot
                                print "TOTAL AMOUNT OF MONEY: ",total_amount
                                print "---------------------------------------------------"
                                dsObject.record_channel_flag[received_snapshot_id] = 0

                            else:
                                #print "Marker received from intermediate channel -- stopping recording for this channel",socket_name_dict[conn]
                                if received_snapshot_id in stop_record:
                                    stop_record[received_snapshot_id][conn] = 1
                                dsObject.snapshot_marker_tracker[received_snapshot_id] += 1
                                print "Value of snapshot marker tracker after incr", dsObject.snapshot_marker_tracker[received_snapshot_id]

                        else: #for initiator , receipt of the first marker executes the below
                            dsObject.snapshot_marker_tracker[received_snapshot_id] = 1
                            #print "SETTING SMT TO 0"

                            stop_record[received_snapshot_id] = {}
                            stop_record[received_snapshot_id][conn] = 1

                    else:
                        # receiving marker for first time from initiator
                        print "Receiving marker from initiator "
                        dsObject.seen_snapshot_ids.append(received_snapshot_id)
                        dsObject.snapshot_marker_tracker[received_snapshot_id] = 1
                        #  record its local state
                        dsObject.local_state_process(received_snapshot_id)
                        # 2 send markers on all outgoing channels
                        dsObject.record_channel_flag[received_snapshot_id] = 1
                        #to prevent messages from the snapshot initiator being added in channel state
                        stop_record[received_snapshot_id] = {}
                        stop_record[received_snapshot_id][conn] = 1


# def get_input_from_user():
#     input_stream = [sys.stdin]
#     read_sockets, write_socket, error_socket = select.select(input_stream, [], [])
#
#     while True:
#         for input in read_sockets:
#             message = sys.stdin.readline()
#             if message == "sn\n":
#                 dsObject.snapshot_algorithm()





id = raw_input("Enter the process id :")
dsObject.process_id = id
with open("config.json", "r") as configFile:
    config = json.load(configFile)
    dsObject.name = config["client_details"][int(id)]["name"]



tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpServer.bind((config["client_details"][int(id)]["ip"], int(config["client_details"][int(id)]["port"])))
tcpServer.listen(5)
#start_new_thread(get_input_from_user, ())
start_new_thread(dsObject.setup_receive_channels, (tcpServer,))
t1 = threading.Thread(target=client_thread, args=())
t1.start()
t1.join()
start_new_thread(dsObject.send_messages,())
start_new_thread(receive_messages, ())
start_new_thread(dsObject.transfer_money,())
print "enter sn for snapshot"
while True:
    message = raw_input()
    if message == "sn":
        dsObject.snapshot_algorithm()
# for idx, val in enumerate(config["client_details"]):
#     if idx != int(id):
#         start_new_thread(client_thread, (val["ip"], int(val["port"]), dsObject.name, val["name"]))

