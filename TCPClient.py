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
#192.168.1.109
parser = argparse.ArgumentParser(description = "TCP-FTP Client - Henri Thomas")
parser.add_argument('-p',"--port",action="store",type=int,help="Server's port number")
parser.add_argument('-f',"--file",action="store",help="Client's requested file to read/write from/to the server")
parser.add_argument('-m',"--mode",choices={'r','w'},help="Client's mode to either read or write to/from the server")
parser.add_argument('-i',"--ip",action="store",help="Client's IP address")
args = parser.parse_args()

#CLOSED
print('client - *closed*')
server_port = args.port
client_port = 0
file_name = args.file
if args.mode == 'r':
    writing = False
else:
    writing = True
host = args.ip
established = False
error = False
block_size = 1024
timeout = 1.0
window_size = 0
client_seq = 200
server_seq = 0
ack = 0
urg = False
done = False
timeout = False
received = bytes()
sending = bytes()
client_packet_manager = TCPPacket()

client_socket = s.socket(s.AF_INET,s.SOCK_DGRAM)
client_socket.settimeout(timeout)
server_address = (host,server_port)
#client_socket.connect((host,server_port))

#******************** 3-WAY HANDSHAKE ********************
if writing:
    urg = True
    f = open(file_name, 'rb')
    sending = client_packet_manager.create_syn_wrq_packet(file_name,0,server_port,client_seq,window_size)
    client_socket.sendto(sending,server_address)
    window_size = randint(4,9)
    client_window = TCPWindow(client_seq,window_size,block_size)
    print('client - write syn sent - seq:',client_seq)
    #client_packet_manager.print_self()
else:
    file_test = Path(file_name)
    if file_test.is_file():
        f = open(file_name + 'CLIENT', 'wb')
    sending = client_packet_manager.create_syn_rrq_packet(file_name,0,server_port,client_seq)
    client_socket.sendto(sending,server_address)
    print('client - read syn sent - seq:',client_seq)

#SYN_SENT
try:
    received, server = client_socket.recvfrom(block_size)
except s.timeout:
    print('client - synack timeout, closing connection')
    f.close()
    client_socket.close()
client_packet_manager.deconstruct_packet(received)
established = True
client_port = client_packet_manager.destination_port.uint
server_seq = client_packet_manager.sequence_number.uint
client_seq = client_packet_manager.ack_number.uint
print('client - server address: ip:',server[0],' port:',server[1])
print('client - synack recevied')
#SEND ACK
ack = server_seq + 1
sending = client_packet_manager.create_ack_packet(client_port,server_port,client_seq,ack,urg,window_size)
client_socket.sendto(sending,server_address)
print('client - synack ack sent - seq:',client_seq,' ack:',ack)

#******************** DATA TRANSFER ********************
#ESTABLISHED
if established:
    print('client - *established*')
    #add file reading/writing and then sliding window
    if writing:
        while not(done):
            if not(client_window.full) and not(timeout):
                #send packet
                print('')
            elif client_window.full and not(timeout):
                #receive ack
                print('')
            elif client_window.full and timeout:
                #resend packet
                print('')
    else:
        #receive packet
        #check packet in order, set booleans
        #write packet data to file
        #send ack
        #but if not in order resend last good ack



#******************** CLOSING SEQUENCE ********************
if writing:
    #FIN_WAIT_1
    print('client - *fin wait 1*')
    client_seq = 400
    ack = 500
    sending = client_packet_manager.create_fin_packet(client_port,server_port,client_seq,ack,urg,window_size)
    client_socket.sendto(sending,server_address)
    print('client - fin wait 1 sent - seq:',client_seq,' ack:',ack,' control:',client_packet_manager.control)

    #FIN_WAIT_2
    print('client - *fin wait 2*')
    try:
        received, server = client_socket.recvfrom(block_size)
    except s.timeout:
        print('client - fin wait 2 timeout, closing connection')
        f.close()
        client_socket.close()
    client_packet_manager.deconstruct_packet(received)
    print('client - fin wait 2 received - seq:',client_packet_manager.sequence_number.uint,' ack:',client_packet_manager.ack_number.uint)

    #TIME_WAIT
    print('client - *time wait*')
    try:
        received, server = client_socket.recvfrom(block_size)
    except s.timeout:
        print('client - last ack timeout, closing connection')
        f.close()
        client_socket.close()
    client_packet_manager.deconstruct_packet(received)
    print('client - last ack received - seq:',client_packet_manager.sequence_number.uint,' ack:',client_packet_manager.ack_number.uint,' control:',client_packet_manager.control)

    client_seq = client_packet_manager.ack_number.uint
    ack = client_packet_manager.sequence_number.uint + 1
    sending = client_packet_manager.create_ack_packet(client_port,server_port,client_seq,ack,urg,window_size)
    client_socket.sendto(sending,server_address)
    print('client - time wait ack sent - seq:',client_seq,' ack:',ack)

else:
    #CLOSE_WAIT
    print('client - *close wait*')
    try:
        received, server = client_socket.recvfrom(block_size)
    except s.timeout:
        print('client - close wait timeout, closing connection')
        f.close()
        client_socket.close()
    client_packet_manager.deconstruct_packet(received)
    print('client - fin wait received - seq:',client_packet_manager.sequence_number.uint,' ack:',client_packet_manager.ack_number.uint,' control:',client_packet_manager.control)

    client_seq = client_packet_manager.ack_number.uint
    ack = client_packet_manager.sequence_number.uint + 1
    sending = client_packet_manager.create_ack_packet(client_port,server_port,client_seq,ack,urg,window_size)
    client_socket.sendto(sending,server_address)
    print('client - close wait ack sent - seq:',client_seq,' ack:',ack)

    #LAST_ACK
    print('client - *last ack*')
    sending = client_packet_manager.create_fin_packet(client_port,server_port,client_seq,ack,urg,window_size)
    client_socket.sendto(sending,server_address)
    print('client - last ack sent - seq:',client_seq,' ack:',ack,' control:',client_packet_manager.control)

    try:
        received, server = client_socket.recvfrom(block_size)
    except s.timeout:
        print('client - time wait ack timeout, closing connection')
        f.close()
        client_socket.close()
    client_packet_manager.deconstruct_packet(received)
    print('client - time wait ack received - seq:',client_packet_manager.sequence_number.uint,' ack:',client_packet_manager.ack_number.uint)

#CLOSED
f.close()
client_socket.close()
print('client - *complete*')
print('client - *closed*')
