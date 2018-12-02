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
import time
import argparse
from pathlib import Path
import random as r
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
block_size = 1400
frame_size = 1472
t = 0.5
last_seq = 0
window_size = 0
server_seq = 300
client_seq = 0
done = False
EOF = False
timeout_bool = False
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
    f = open('serverfile', 'wb')
    urg = True
else:
    #writing to client
    f = open('test2.txt', 'rb')
    urg = False
    writing = True
    window_size = r.randint(4,9)
    server_socket.settimeout(t)
    server_timer = TCPTimer(t,window_size)
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
            if not(timeout_bool) and not(server_window.full):
                ack += 1
                #send packet
                d = f.read(block_size)
                server_window.update_window(server_seq,ack)
                sending = server_packet_manager.create_data_packet(server_port,client_port,server_seq,ack,urg,window_size,d)
                print('\tserver - sending packet - seq:',server_seq,' ack:',ack)
                server_seq += block_size
                if d.decode() == "":
                    last_seq = server_seq
                    EOF = True
                    #print('server - last seq:',last_seq)
                server_timer.start_new_timer()
                server_socket.sendto(sending,client)
            elif not(timeout_bool) and server_window.full:
                #check timeout
                    #print('\tclient - times:',client_timer.times)
                    if time.time() - server_timer.times[0] > t:
                        timeout_bool = True
                        print('\tserver - ack timeout on timer')
                    if timeout_bool == False:
                        #receive ack
                        try:
                            received, client = server_socket.recvfrom(frame_size)
                        except s.timeout:
                            timeout_bool = True
                            print('\tserver - ack timeout on socket')

                        if timeout_bool == False:
                            server_packet_manager.deconstruct_packet(received)
                            if server_packet_manager.ack_number.uint == last_seq:
                                done = True
                                #print('server - received last ack')
                            if not(EOF):
                                shift = server_window.shift_window_helper(server_packet_manager.ack_number.uint)
                                for i in range(0,shift):
                                    server_window.shift_window()
                                    server_timer.shift_times()
                            #print('\tserver - received ack - seq:',server_packet_manager.sequence_number.uint,' ack:',server_packet_manager.ack_number.uint,' window:',server_window.sequence_array)
            elif timeout_bool:
                #resend packet
                print('\tserver - resending packets - seqs:',server_window.sequence_array[0],' -',server_window.sequence_array[window_size - 1])
                server_timer.clear_times()
                f.seek(server_window.file_offset)
                for i in range(0,window_size):
                    if server_window.sequence_array[i] == 0:
                        #ack = client_window.ack_array[i-1] + 1
                        pos = i - 1
                        break
                    d = f.read(block_size)
                    sending = server_packet_manager.create_data_packet(server_port,client_port,server_window.sequence_array[i],server_window.ack_array[i],urg,window_size,d)
                    server_socket.sendto(sending,client)
                    print('\tserver - resending packet - seq:',server_window.sequence_array[i],' ack:',server_window.ack_array[i])
                    #ack += 1
                    server_timer.start_new_timer()
                #ack = client_window.ack_array[pos] + 1
                timeout_bool = False
            else:
                print('\tserver - waiting')
    else:
        while not(done):
            #receive packet
            received, client = server_socket.recvfrom(frame_size)
            server_packet_manager.deconstruct_packet(received)
            if server_packet_manager.control == '0b110001' or server_packet_manager.control == '0b010001':
                done = True
            #check for errors
            #client_checksum = server_packet_manager.checksum.uint
            #server_packet_manager.set_checksum(0)
            #server_checksum = binascii.crc32(server_packet_manager.byte_form())
            #server_checksum = binascii.crc_hqx(server_packet_manager.byte_form(),server_checksum)
            #check packet in order
            if not(done):
                if server_packet_manager.sequence_number.uint == client_seq and error == False:
                    if r.random() < 0.93:
                        #increment for the expected next client seq for ack packet
                        client_seq += block_size
                        #write packet data to file
                        f.write(server_packet_manager.data.tobytes())
                        #send new ack
                        server_seq = server_packet_manager.ack_number.uint#+=1
                        print('\tserver - sending ack - seq:',server_seq,' ack:',client_seq)
                        sending = server_packet_manager.create_ack_packet(server_port,client_port,server_seq,client_seq,urg,window_size)
                        server_socket.sendto(sending,client)
                        #error = False
                else:
                    #resend last ack
                    print('\tserver - resending ack - seq:',server_seq,' ack:',client_seq)
                    sending = server_packet_manager.create_ack_packet(server_port,client_port,server_seq,client_seq,urg,window_size)
                    server_socket.sendto(sending,client)



#******************** CLOSING SEQUENCE ********************
f.close()
if writing:
    #FIN_WAIT_1
    print('server - *fin wait 1*')
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
    #received, client = server_socket.recvfrom(frame_size)
    #server_packet_manager.deconstruct_packet(received)
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
print('server - *complete*')
print('server - *closed*')
time.sleep(1)
server_socket.close()
quit()

"""

try:
    received, server = server_socket.recvfrom(frame_size)
    except s.timeout:
        timeout_bool = True
        print('\tclient - ack timeout on socket')

        if timeout_bool == False:
            server_packet_manager.deconstruct_packet(received)
            print('\tclient - received ack - seq:',client_packet_manager.sequence_number.uint,' ack:',client_packet_manager.ack_number.uint)
            if client_packet_manager.ack_number.uint == last_ack:
                done = True
                shift = client_window.shift_window_helper(client_packet_manager.ack_number.uint)
                for i in range(0,shift):
                    client_window.shift_window()
                    client_timer.shift_times()



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
"""
