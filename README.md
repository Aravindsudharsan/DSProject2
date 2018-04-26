# DSProject2

The aim of the project was to simulate bank transactions in distributed systems
Every client in the system will transfer random money at a specified interval of time
A snapshot can be taken at any instant at a client and the snapshot contains both received and sent money at the client where snapshot is taken and also the money on the fly which is the money deduced but not posted
The purpose of this snapshot is that states of the client can be retrieved in case of site failures
The application was implemented in Python

The config.json file contains the data center's details namely IP and port number
The clientprog.py file has the logic for establing connection between the cllient and server and then perform snapshot algorithm
