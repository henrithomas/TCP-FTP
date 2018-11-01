# -*- coding: utf-8 -*-
"""
Henri Thomas
Computer Networks
Assignment 2
"""
#from socket import *
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
#run in background on windows: start /b python script.py
parser = argparse.ArgumentParser(description = "TCP-FTP Client - Henri Thomas")
parser.add_argument('-p',"--port",action="store",type=int,help="Server's port number")
args = parser.parse_args()

#CLOSED
print('server - *closed*')
server_port = args.port
client_port = 0
host = s.gethostname()
writing = False
established = False
error = False
block_size = 1024
timeout = 0.5
window_size = 0
server_seq = 300
client_seq = 0
ack = 0
received = bytes()
sending = bytes()
server_packet_manager = TCPPacket()

#LISTEN
server_socket = s.socket(s.AF_INET,s.SOCK_DGRAM)
print('server - *ready to receive*')
server_socket.bind((host,server_port))
#server_socket.settimeout(timeout)

#******************** 3-WAY HANDSHAKE ********************
#SYN_RCVD
received, client = server_socket.recvfrom(block_size)
server_packet_manager.deconstruct_packet(received)
print('server - client address: ip:',client[0],' port:',client[1])
client_port = client[1]
client_seq = server_packet_manager.sequence_number.uint
client_control_bits = server_packet_manager.control
if client_control_bits[0] == True:
    urg = True
else:
    urg = False
    writing = True
    window_size = randint(4,9)
client_window_size = server_packet_manager.window.uint

ack = client_seq + 1
sending = server_packet_manager.create_synack_packet(server_port,client_port,server_seq,ack,urg,client_window_size)
server_socket.sendto(sending,client)
print('server - synack sent - seq:',server_seq,'ack:',ack)

received, client = server_socket.recvfrom(block_size)
server_packet_manager.deconstruct_packet(received)
established = True
print('server - synack ack received')

#******************** DATA TRANSFER ********************
#ESTABLISHED
if established:
    print('server - *established*')
    #add file reading/writing and then sliding window
    
    
    
    
     
#******************** CLOSING SEQUENCE ********************
if writing:
    #FIN_WAIT_1
    print('server - *fin wait 1*')
    server_seq = 400
    ack = 500
    sending = server_packet_manager.create_fin_packet(server_port,client_port,server_seq,ack,urg,window_size)
    server_socket.sendto(sending,client)
    print('server - fin wait 1 sent - seq:',server_seq,' ack:',ack,' control:',server_packet_manager.control)
    
    #FIN_WAIT_2
    print('server - *fin wait 2*')
    received, client = server_socket.recvfrom(block_size)
    server_packet_manager.deconstruct_packet(received)
    print('server - fin wait 2 received - seq:',server_packet_manager.sequence_number.uint,' ack:',server_packet_manager.ack_number.uint)
    
    #TIME_WAIT
    print('server - *time wait*')
    received, client = server_socket.recvfrom(block_size)
    server_packet_manager.deconstruct_packet(received)
    print('server - time wait received - seq:',server_packet_manager.sequence_number.uint,' ack:',server_packet_manager.ack_number.uint)
    
    server_seq = server_packet_manager.ack_number.uint
    ack = server_packet_manager.sequence_number.uint + 1
    sending = server_packet_manager.create_ack_packet(server_port,client_port,server_seq,ack,urg,window_size)
    server_socket.sendto(sending,client)
    print('server - time wait ack sent - seq:',server_seq,' ack:',ack)
else:
    #CLOSE_WAIT
    print('server - *close wait*')
    received, client = server_socket.recvfrom(block_size)
    server_packet_manager.deconstruct_packet(received)
    print('server - fin wait received - seq:',server_packet_manager.sequence_number.uint,' ack:',server_packet_manager.ack_number.uint,' control:',server_packet_manager.control)
    
    server_seq = server_packet_manager.ack_number.uint
    ack = server_packet_manager.sequence_number.uint + 1
    sending = server_packet_manager.create_ack_packet(server_port,client_port,server_seq,ack,urg,window_size)
    server_socket.sendto(sending,client)
    print('server - close wait ack sent - seq:',server_seq,' ack:',ack)
    
    #lAST_ACK
    print('server - *last ack*')
    sending = server_packet_manager.create_fin_packet(server_port,client_port,server_seq,ack,urg,window_size)
    server_socket.sendto(sending,client)
    print('server - last ack sent - seq:',server_seq,' ack:',ack,' control:',server_packet_manager.control)
    
    received, client = server_socket.recvfrom(block_size)
    server_packet_manager.deconstruct_packet(received)
    print('server - time wait ack received - seq:',server_packet_manager.sequence_number.uint,' ack:',server_packet_manager.ack_number.uint)
    
#CLOSED
server_socket.close()
print('server - *complete*')
print('server - *closed*')