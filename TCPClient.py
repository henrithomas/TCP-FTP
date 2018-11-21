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
import time
from pathlib import Path
import random as r
#STATES: CLOSED, SYN_SENT, ESTABLISHED, FIN_WAIT_1,
#        FIN_WAIT_2, TIME_WAIT
#192.168.1.46
#172.16.54.29
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
block_size = 1400
frame_size = 1472
t = 0.5
window_size = 0
client_seq = 200
server_seq = 0
ack = 0
last_seq = 0
shift = 0
urg = False
done = False
EOF = False
timeout_bool = False
received = bytes()
sending = bytes()
d = bytes()
client_packet_manager = TCPPacket()

client_socket = s.socket(s.AF_INET,s.SOCK_DGRAM)
server_address = (host,server_port)
#client_socket.connect((host,server_port))

#******************** 3-WAY HANDSHAKE ********************
if writing:
    urg = True
    f = open(file_name, 'rb')
    sending = client_packet_manager.create_syn_wrq_packet(file_name,0,server_port,client_seq,window_size)
    client_socket.sendto(sending,server_address)
    window_size = r.randint(4,9)
    #window_size = 9
    client_window = TCPWindow(client_seq,window_size,block_size)
    client_window.set_base(client_seq)
    client_window.set_file_offset(0)
    client_socket.settimeout(0.5)
    client_timer = TCPTimer(timeout_bool,window_size)
    print('client - window size:',window_size)
    print('client - sending length:',len(sending), 'file:',file_name)
    print('client - write syn sent - seq:',client_seq)
    #client_packet_manager.print_self()
else:
    file_test = Path(file_name)
    if file_test.is_file():
        f = open('clientfile', 'wb')
    sending = client_packet_manager.create_syn_rrq_packet(file_name,0,server_port,client_seq)
    client_socket.sendto(sending,server_address)
    print('client - read syn sent - seq:',client_seq)

#SYN_SENT
try:
    received, server = client_socket.recvfrom(frame_size)
except s.timeout:
    print('client - synack timeout, closing connection')
    f.close()
    client_socket.close()
client_packet_manager.deconstruct_packet(received)
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
established = True
ack -= 1
#******************** DATA TRANSFER ********************
#ESTABLISHED
if established:
    print('\tclient - *established*')
    #add file reading/writing and then sliding window
    if writing:
        while not(done):
            if not(timeout_bool) and not(client_window.full):
                ack += 1
                #send packet
                d = f.read(block_size)
                client_window.update_window(client_seq,ack)
                sending = client_packet_manager.create_data_packet(client_port,server_port,client_seq,ack,urg,window_size,d)
                print('\tclient - sending packet - seq:',client_seq,' ack:',ack)
                client_seq += block_size
                if d.decode() == "":
                    last_seq = client_seq
                    EOF = True
                    #print('client - last seq:',last_seq)
                client_timer.start_new_timer()
                client_socket.sendto(sending,server_address)
            elif not(timeout_bool) and client_window.full:
                #check timeout
                    #print('\tclient - times:',client_timer.times)
                    if time.time() - client_timer.times[0] > t:
                        timeout_bool = True
                        print('\tclient - ack timeout on timer')
                    if timeout_bool == False:
                        #receive ack
                        try:
                            received, server = client_socket.recvfrom(frame_size)
                        except s.timeout:
                            timeout_bool = True
                            print('\tclient - ack timeout on socket')
                    
                        if timeout_bool == False:
                            client_packet_manager.deconstruct_packet(received)
                            if client_packet_manager.ack_number.uint == last_seq:
                                done = True
                                #print('client - received last ack')
                            if not(EOF):
                                shift = client_window.shift_window_helper(client_packet_manager.ack_number.uint)
                                for i in range(0,shift):    
                                    client_window.shift_window()
                                    client_timer.shift_times()
                            #print('\tclient - received ack - seq:',client_packet_manager.sequence_number.uint,' ack:',client_packet_manager.ack_number.uint,' window:',client_window.sequence_array)
            elif timeout_bool:
                #resend packet
                print('\tclient - resending packets - seqs:',client_window.sequence_array[0],' -',client_window.sequence_array[window_size - 1])
                client_timer.clear_times()
                f.seek(client_window.file_offset)
                for i in range(0,window_size):
                    if client_window.sequence_array[i] == 0:
                        #ack = client_window.ack_array[i-1] + 1
                        pos = i - 1
                        break
                    d = f.read(block_size)
                    sending = client_packet_manager.create_data_packet(client_port,server_port,client_window.sequence_array[i],client_window.ack_array[i],urg,window_size,d)
                    client_socket.sendto(sending,server_address)
                    print('\tclient - resending packet - seq:',client_window.sequence_array[i],' ack:',client_window.ack_array[i])
                    #ack += 1
                    client_timer.start_new_timer()
                #ack = client_window.ack_array[pos] + 1
                timeout_bool = False
            else:
                print('\tclient - waiting')
    else:
        while not(done):
            #receive packet
            received, server = client_socket.recvfrom(frame_size)
            client_packet_manager.deconstruct_packet(received)
            if client_packet_manager.control == '0b110001' or client_packet_manager.control == '0b010001':
                done = True
            #check for errors
            #check packet in order
            if not(done):
                if client_packet_manager.sequence_number.uint == server_seq and error == False:
                    if r.random() < 0.93:               
                        #increment for the expected next client seq for ack packet
                        server_seq += block_size
                        #write packet data to file
                        f.write(client_packet_manager.data.tobytes())
                        #send new ack
                        client_seq = client_packet_manager.ack_number.uint#+=1  
                        print('\tclient - sending ack - seq:',client_seq,' ack:',server_seq)
                        sending = client_packet_manager.create_ack_packet(client_port,server_port,client_seq,server_seq,urg,window_size)
                        client_socket.sendto(sending,server)
                        #error = False
                else:
                    #resend last ack
                    print('\tclient - resending ack - seq:',client_seq,' ack:',server_seq)
                    sending = client_packet_manager.create_ack_packet(client_port,server_port,client_seq,server_seq,urg,window_size)
                    client_socket.sendto(sending,server)

#******************** CLOSING SEQUENCE ********************
f.close()
if writing:
    #FIN_WAIT_1
    print('client - *fin wait 1*')
    sending = client_packet_manager.create_fin_packet(client_port,server_port,client_seq,ack,urg,window_size)
    client_socket.sendto(sending,server_address)
    print('client - fin wait 1 sent - seq:',client_seq,' ack:',ack,' control:',client_packet_manager.control)

    #FIN_WAIT_2
    print('client - *fin wait 2*')
    try:
        received, server = client_socket.recvfrom(frame_size)
    except s.timeout:
        print('client - fin wait 2 timeout, closing connection')
        f.close()
        client_socket.close()
    client_packet_manager.deconstruct_packet(received)
    print('client - fin wait 2 received - seq:',client_packet_manager.sequence_number.uint,' ack:',client_packet_manager.ack_number.uint)

    #TIME_WAIT
    print('client - *time wait*')
    try:
        received, server = client_socket.recvfrom(frame_size)
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
    """
    try:
        received, server = client_socket.recvfrom(frame_size)
    except s.timeout:
        print('client - close wait timeout, closing connection')
        f.close()
        client_socket.close()
    client_packet_manager.deconstruct_packet(received)
    """
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
        received, server = client_socket.recvfrom(frame_size)
    except s.timeout:
        print('client - time wait ack timeout, closing connection')
        f.close()
        client_socket.close()
    client_packet_manager.deconstruct_packet(received)
    print('client - time wait ack received - seq:',client_packet_manager.sequence_number.uint,' ack:',client_packet_manager.ack_number.uint)

#CLOSED
print('client - *complete*')
print('client - *closed*')
time.sleep(1)
client_socket.close()
quit()

"""
                try:
                    received, server = client_socket.recvfrom(frame_size)
                except s.timeout:
                    timeout_bool = True
                    print('\tclient - ack timeout on socket')
                
                if timeout_bool == False:
                    client_packet_manager.deconstruct_packet(received)
                    print('\tclient - received ack - seq:',client_packet_manager.sequence_number.uint,' ack:',client_packet_manager.ack_number.uint)
                    if client_packet_manager.ack_number.uint == last_ack:
                        done = True
                    shift = client_window.shift_window_helper(client_packet_manager.ack_number.uint)
                    for i in range(0,shift):    
                        client_window.shift_window()
                        client_timer.shift_times()
"""