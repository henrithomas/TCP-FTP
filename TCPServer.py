# -*- coding: utf-8 -*-
"""
Henri Thomas
Computer Networks
Assignment 2
"""
from socket import *
import socket as s
from TCPPacket import TCPPacket
from TCPWindow import TCPWindow
from TCPTimer import TCPTimer
from bitstring import BitArray
import argparse
from pathlib import Path
from random import randint
#STATES: CLOSED, SYN_SENT, ESTABLISHED, FIN_WAIT_1,
#        FIN_WAIT_2, TIME_WAIT

parser = argparse.ArgumentParser(description = "TCP-FTP Client - Henri Thomas")
parser.add_argument('-p',"--port",action="store",type=int,help="Server's port number")
args = parser.parse_args()

#CLOSED
server_port = args.port
host = s.gethostname()
established = False
error = False
block_size = 1024
timeout = 0.5
window_size = 0
server_isn = 300
received = bytes()
sending = bytes()
server_packet_manager = TCPPacket()

#LISTEN
server_socket = socket(AF_INET,SOCK_DGRAM)
server_socket.bind((host,server_port))
#server_socket.settimeout(timeout)

#SYN_RCVD
received, client = server_socket.recvfrom(block_size)
server_packet_manager.deconstruct_packet(received)
established = True
print('server - client address check: ip',client[0],' port',client[1])
    
client_seq = server_packet_manager.sequence_number
client_control_bits = server_packet_manager.control
if client_control_bits[0] == True:
    urg = True
else:
    urg = False
    window_size = randint(4,9)
client_window_size = server_packet_manager.window.int

sending = server_packet_manager.create_synack_packet(server_port,0,server_isn,(client_seq + block_size),urg,window_size)
server_socket.sendto(sending,client)

#ESTABLISHED

#CLOSE_WAIT

#lAST_ACK

#CLOSED
server_socket.close()
print('server - complete')
print('server - closed')