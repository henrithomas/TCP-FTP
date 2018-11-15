# -*- coding: utf-8 -*-
"""
Henri Thomas
Computer Networks
Assignment 2
"""
#from socket import *
import socket as s
import binascii
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
client_checksum = 0
server_checksum = 0
block_size = 1024
frame_size = 1472
timeout = 1.0
window_size = 0
server_seq = 300
client_seq = 0
done = False
timeout = False
#error = False
ack = 0
received = bytes()
sending = bytes()
server_packet_manager = TCPPacket()

#LISTEN
server_socket = s.socket(s.AF_INET,s.SOCK_DGRAM)
print('server - *ready to receive*')
server_socket.bind((host,server_port))


#******************** 3-WAY HANDSHAKE ********************
#SYN_RCVD
try:
    received, client = server_socket.recvfrom(frame_size)
except s.timeout:
    print('server - syn receive timeout')
server_packet_manager.deconstruct_packet(received)
#server_socket.settimeout(timeout)
print('server - client address: ip:',client[0],' port:',client[1])
client_port = client[1]
client_seq = server_packet_manager.sequence_number.uint
client_control_bits = server_packet_manager.control

if client_control_bits[0] == True:
    #reading from client
    file_name = server_packet_manager.data.tobytes().decode()
    print('server - file:',file_name)
    f = open('serverfile.txt', 'wb')
    urg = True
else:
    #writing to client
    f = open(server_packet_manager.file_name, 'rb')
    urg = False
    writing = True
    window_size = randint(4,9)
    #server_socket.settimeout(timeout)
    server_timer = TCPTimer(timeout,window_size)
    server_window = TCPWindow(server_seq,window_size,block_size)
client_window_size = server_packet_manager.window.uint

ack = client_seq + 1
sending = server_packet_manager.create_synack_packet(server_port,client_port,server_seq,ack,urg,client_window_size)
print('server - sending length:',len(sending))
server_socket.sendto(sending,client)
print('server - synack sent - seq:',server_seq,'ack:',ack)

received, client = server_socket.recvfrom(frame_size)
server_packet_manager.deconstruct_packet(received)
client_seq = server_packet_manager.sequence_number.uint
established = True
print('server - synack ack received')

#******************** DATA TRANSFER ********************
#ESTABLISHED
if established:
    print('\tserver - *established*')
    #add file reading/writing and then sliding window
    if writing:
        while not(done):
            if not(server_window.full) and not(timeout):
                #send packet
                print('')
            elif server_window.full and not(timeout):
                #receive ack
                 print('')
                 try:
                     received, client = server_socket.recvfrom(frame_size)
                     timeout = False
                     print('\tserver ack received')
                 except s.timeout:
                     timeout = True
                     print('\tserver - packet timeout')
            elif server_window.full and timeout:
                #resend packets
                 print('')
            else:
                #wait
                print('\tserver - waiting')
    else:
        while not(done):
            #receive packet
            received, client = server_socket.recvfrom(frame_size)
            server_packet_manager.deconstruct_packet(received)
            print('\tserver - received packet - seq:',server_packet_manager.sequence_number.uint,' ack:',server_packet_manager.ack_number.uint)
            if len(server_packet_manager.data) < block_size:
                done = True
            #check for errors
            client_checksum = server_packet_manager.checksum.uint
            server_checksum = binascii.crc32(server_packet_manager.data.tobytes())
            server_checksum = binascii.crc_hqx(server_packet_manager.data.tobytes(),server_checksum)
            #if client_checksum != server_checksum:
            #    error = True
            #check packet in order, set booleans
            #print('\tserver - client_seq:',client_seq,' received sequence:',server_packet_manager.sequence_number.uint)
            if not(done):
                if server_packet_manager.sequence_number.uint == client_seq and error == False:
                    #increment for the expected next client seq for ack packet
                    client_seq += block_size
                    #write packet data to file
                    f.write(server_packet_manager.data.tobytes())
                    #send new ack
                    server_seq = server_packet_manager.ack_number.uint
                    print('\tserver - sending ack - seq:',server_seq,' ack:',client_seq)
                    sending = server_packet_manager.create_ack_packet(server_port,client_port,server_seq,client_seq,urg,window_size)
                    server_socket.sendto(sending,client)
                    #error = False
                else:
                    #resend last ack
                    #server_seq = server_packet_manager.ack_number.uint
                    print('\tserver - resending ack - seq:',server_seq,' ack:',client_seq)
                    sending = server_packet_manager.create_ack_packet(server_port,client_port,server_seq,client_seq,urg,window_size)
                    server_socket.sendto(sending,client)



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
    received, client = server_socket.recvfrom(frame_size)
    server_packet_manager.deconstruct_packet(received)
    print('server - fin wait 2 received - seq:',server_packet_manager.sequence_number.uint,' ack:',server_packet_manager.ack_number.uint)

    #TIME_WAIT
    print('server - *time wait*')
    received, client = server_socket.recvfrom(frame_size)
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
    received, client = server_socket.recvfrom(frame_size)
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

    received, client = server_socket.recvfrom(frame_size)
    server_packet_manager.deconstruct_packet(received)
    print('server - time wait ack received - seq:',server_packet_manager.sequence_number.uint,' ack:',server_packet_manager.ack_number.uint)

#CLOSED
server_socket.close()
print('server - *complete*')
print('server - *closed*')
