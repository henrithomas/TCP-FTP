# -*- coding: utf-8 -*-
"""
Henri Thomas
Computer Networks
Assignment 2
"""
from bitstring import BitArray
import binascii

class TCPPacket:
    #header and data
    """
    source_port = BitArray('0x0000')
    destination_port = BitArray('0x0000')
    sequence_number = BitArray('0x00000000')
    ack_number = BitArray('0x00000000')
    data_offset = BitArray('0x6')
    reserved = BitArray('0b000000')
    control = BitArray('0b000000')
    window = BitArray('0x0000')
    checksum =  BitArray('0x0000')
    urgent_pointer = BitArray('0x0000')
    options = BitArray('0x000000')
    padding = BitArray('0x0000')
    data = BitArray('0x00000000')
    file_name = ''
    """
    def __init__(self):
        self.source_port = BitArray('0x0000')
        self.destination_port = BitArray('0x0000')
        self.sequence_number = BitArray('0x00000000')
        self.ack_number = BitArray('0x00000000')
        self.data_offset = BitArray('0x6')
        self.reserved = BitArray('0b000000')
        self.control = BitArray('0b000000')
        self.window = BitArray('0x0000')
        self.checksum =  BitArray('0x0000')
        self.urgent_pointer = BitArray('0x0000')
        self.options = BitArray('0x000000')
        self.padding = BitArray('0x0000')
        self.data = BitArray('0x00000000')
        self.file_name = ''
        self.crc = 0

    #method to ensure proper hex string length
    def full_hex(self,s,size):
        return '0x' + s[2:].zfill(size)

    #extract strings from request
    def extract_string(self,data,start):
        seeking = True
        i = start
        while seeking == True:
            if data[i] == 0:
                seeking = False
            else:
                i += 1
        name = data[start:i]
        return name.decode()

    #SET methods
    def set_source_port(self,val):
        self.source_port = BitArray(self.full_hex(hex(val),4))

    def set_destination_port(self,val):
        self.destination_port = BitArray(self.full_hex(hex(val),4))

    def set_sequence_number(self,val):
        self.sequence_number = BitArray(self.full_hex(hex(val),4))

    def set_ack_number(self,val):
        self.ack_number = BitArray(self.full_hex(hex(val),4))

    def set_data_offset(self,val):
        self.data_offset = BitArray(self.full_hex(hex(val),2))

    def set_reserved(self,val):
        self.reserved = val

    def set_control(self,val):
        self.control = val

    def set_window(self,val):
        self.window = val

    def set_checksum(self,val):
        self.checksum = BitArray(self.full_hex(hex(val),4))

    def set_urgent_pointer(self,val):
        self.urgent_pointer = BitArray(self.full_hex(hex(val),4))

    def set_data(self,val):
        self.data = val

    #GET methods
    def get_source_port(self,val):
        return self.source_port

    def get_destination_port(self,val):
        return self.destination_port

    def get_sequence_number(self,val):
        return self.sequence_number

    def get_ack_number(self,val):
        return self.ack_number

    def get_data_offset(self,val):
        return self.data_offset

    def get_reserved(self,val):
        return self.reserved

    def get_control(self,val):
        return self.control

    def get_window(self,val):
        return self.window

    def get_checksum(self,val):
        return self.checksum

    def get_urgent_pointer(self,val):
        return self.urgent_pointer

    def get_data(self,val):
        return self.data

    #form a RRQ packet
    def create_syn_rrq_packet(self,name,source,dest,seq):
        self.source_port = BitArray(self.full_hex(hex(source),4))
        self.destination_port = BitArray(self.full_hex(hex(dest),4))
        self.sequence_number = BitArray(self.full_hex(hex(seq),8))
        self.window = BitArray(self.full_hex(hex(0),4))
        #syn = 1, read/urg = 0
        self.control = BitArray('0b000010')
        self.file_name = name
        file = BitArray(name.encode())
        #create packet string
        pkt = self.source_port
        pkt.append(self.destination_port)
        pkt.append(self.sequence_number)
        pkt.append(self.ack_number)
        pkt.append(self.data_offset)
        pkt.append(self.reserved)
        pkt.append(self.control)
        pkt.append(self.window)
        pkt.append(self.checksum)
        pkt.append(self.urgent_pointer)
        pkt.append(self.options)
        pkt.append(self.padding)
        pkt.append(file)

        return pkt.tobytes()

    #form a WRQ packet
    def create_syn_wrq_packet(self,name,source,dest,seq,window):
        self.source_port = BitArray(self.full_hex(hex(source),4))
        self.destination_port = BitArray(self.full_hex(hex(dest),4))
        self.sequence_number = BitArray(self.full_hex(hex(seq),8))
        self.window = BitArray(self.full_hex(hex(window),4))
        #syn = 1, read/urg = 1
        self.control = BitArray('0b100010')
        self.file_name = name
        file = BitArray(name.encode())
        #create packet string
        pkt = self.source_port
        pkt.append(self.destination_port)
        pkt.append(self.sequence_number)
        pkt.append(self.ack_number)
        pkt.append(self.data_offset)
        pkt.append(self.reserved)
        pkt.append(self.control)
        pkt.append(self.window)
        pkt.append(self.checksum)
        pkt.append(self.urgent_pointer)
        pkt.append(self.options)
        pkt.append(self.padding)
        pkt.append(file)

        return pkt.tobytes()

    def create_synack_packet(self,source,dest,seq,ack,urg,window):
        self.source_port = BitArray(self.full_hex(hex(source),4))
        self.destination_port = BitArray(self.full_hex(hex(dest),4))
        self.sequence_number = BitArray(self.full_hex(hex(seq),8))
        self.ack_number = BitArray(self.full_hex(hex(ack),8))
        self.window = BitArray(self.full_hex(hex(window),4))
        self.data = BitArray('0x00000000')
        #send r/w, syn, and ack flags
        if urg:
            self.control = BitArray('0b110010')
        else:
            self.control = BitArray('0b010010')
        #create packet string
        pkt = self.source_port
        pkt.append(self.destination_port)
        pkt.append(self.sequence_number)
        pkt.append(self.ack_number)
        pkt.append(self.data_offset)
        pkt.append(self.reserved)
        pkt.append(self.control)
        pkt.append(self.window)
        pkt.append(self.checksum)
        pkt.append(self.urgent_pointer)
        pkt.append(self.options)
        pkt.append(self.padding)
        pkt.append(self.data)

        return pkt.tobytes()

    def create_ack_packet(self,source,dest,seq,ack,urg,window):
        self.source_port = BitArray(self.full_hex(hex(source),4))
        self.destination_port = BitArray(self.full_hex(hex(dest),4))
        self.sequence_number = BitArray(self.full_hex(hex(seq),8))
        self.ack_number = BitArray(self.full_hex(hex(ack),8))
        self.window = BitArray(self.full_hex(hex(window),4))
        self.data = BitArray('0x00000000')
        #send r/w and ack flags
        if urg:
            self.control = BitArray('0b110000')
        else:
            self.control = BitArray('0b010000')
        #create packet string
        pkt = self.source_port
        pkt.append(self.destination_port)
        pkt.append(self.sequence_number)
        pkt.append(self.ack_number)
        pkt.append(self.data_offset)
        pkt.append(self.reserved)
        pkt.append(self.control)
        pkt.append(self.window)
        pkt.append(self.checksum)
        pkt.append(self.urgent_pointer)
        pkt.append(self.options)
        pkt.append(self.padding)
        pkt.append(self.data)

        return pkt.tobytes()

    def create_data_packet(self,source,dest,seq,ack,urg,window,dat):
        self.source_port = BitArray(self.full_hex(hex(source),4))
        self.destination_port = BitArray(self.full_hex(hex(dest),4))
        self.sequence_number = BitArray(self.full_hex(hex(seq),8))
        self.ack_number = BitArray(self.full_hex(hex(ack),8))
        self.window = BitArray(self.full_hex(hex(window),4))
        self.checksum =  BitArray(self.full_hex(hex(0),4))
        self.data = BitArray(dat)
        #send r/w and ack flags
        if urg:
            self.control = BitArray('0b100000')
        else:
            self.control = BitArray('0b000000')

        #create packet string
        pkt = self.source_port
        pkt.append(self.destination_port)
        pkt.append(self.sequence_number)
        pkt.append(self.ack_number)
        pkt.append(self.data_offset)
        pkt.append(self.reserved)
        pkt.append(self.control)
        pkt.append(self.window)
        pkt.append(self.checksum)
        pkt.append(self.urgent_pointer)
        pkt.append(self.options)
        pkt.append(self.padding)
        pkt.append(self.data)

        #create checksum
        self.crc = binascii.crc32(pkt.tobytes())
        self.crc = binascii.crc_hqx(pkt.tobytes(),self.crc)
        self.checksum = BitArray(self.full_hex(hex(self.crc),4))
        pkt[128:144] = self.checksum
        #self.checksum = BitArray(dat[16:18])
        return pkt.tobytes()

    def create_fin_packet(self,source,dest,seq,ack,urg,window):
        self.source_port = BitArray(self.full_hex(hex(source),4))
        self.destination_port = BitArray(self.full_hex(hex(dest),4))
        self.sequence_number = BitArray(self.full_hex(hex(seq),8))
        self.ack_number = BitArray(self.full_hex(hex(ack),8))
        self.window = BitArray(self.full_hex(hex(window),4))
        self.data = BitArray('0x00000000')
        #send fin, r/w and ack flags
        if urg:
            self.control = BitArray('0b110001')
        else:
            self.control = BitArray('0b010001')
        #create packet string
        pkt = self.source_port
        pkt.append(self.destination_port)
        pkt.append(self.sequence_number)
        pkt.append(self.ack_number)
        pkt.append(self.data_offset)
        pkt.append(self.reserved)
        pkt.append(self.control)
        pkt.append(self.window)
        pkt.append(self.checksum)
        pkt.append(self.urgent_pointer)
        pkt.append(self.options)
        pkt.append(self.padding)
        pkt.append(self.data)

        return pkt.tobytes()

    #deconstruct a packet
    def deconstruct_packet(self, dat):
        self.source_port = BitArray(dat[0:2])
        self.destination_port = BitArray(dat[2:4])
        self.sequence_number = BitArray(dat[4:8])
        self.ack_number = BitArray(dat[8:12])
        temp = BitArray(dat[13:14])
        self.control = temp[2:8]
        if self.control == BitArray('0b000010') or self.control == BitArray('0b100010'):
            self.file_name = dat[24:].decode()
        del temp
        self.window = BitArray(dat[14:16])
        self.checksum = BitArray(dat[16:18])
        self.data = BitArray(dat[24:])

    def byte_form(self):
        #create packet string
        pkt = self.source_port
        pkt.append(self.destination_port)
        pkt.append(self.sequence_number)
        pkt.append(self.ack_number)
        pkt.append(self.data_offset)
        pkt.append(self.reserved)
        pkt.append(self.control)
        pkt.append(self.window)
        pkt.append(self.checksum)
        pkt.append(self.urgent_pointer)
        pkt.append(self.options)
        pkt.append(self.padding)
        pkt.append(self.data)

        return pkt.tobytes()

    def print_self(self):
        print('packet source port:',self.source_port.uint)
        print('packet destination port:',self.destination_port.uint)
        print('packet sequence number:',self.sequence_number.uint)
        print('packet acknowledgment number:',self.ack_number.uint)
        print('packet data offset:',self.data_offset.uint)
        print('packet reserved:',self.reserved.uint)
        print('packet control bits:',self.control)
        print('packet window:',self.window.uint)
        print('packet checksum',self.checksum.uint)
        print('packet urgent pointer:',self.urgent_pointer.uint)
        print('packet options:',self.options.uint)
        print('packet padding',self.padding)
        print('packet data:',self.data.tobytes().decode())

    #class main method
    def main(self):
        print('TCP Packet')

if __name__ == "__main__":
    print('TCP Packet')
    """
    P = TCPPacket()
    #P.main()

    s = 'hello.txt'
    data = s.encode()
    p_test = TCPPacket()

    print('syn rrq test')
    p_test.deconstruct_packet(P.create_syn_rrq_packet(s,151,320,100))
    p_test.print_self()
    print('\nsyn wrq test')
    p_test.deconstruct_packet(P.create_syn_wrq_packet(s,151,320,100,6))
    p_test.print_self()
    print('\nsynack test')
    p_test.deconstruct_packet(P.create_synack_packet(1002,3456,300,101,True,6))
    p_test.print_self()
    print('\nack test')
    p_test.deconstruct_packet(P.create_ack_packet(3456,1002,101,301,True,6))
    p_test.print_self()

    print('\ndata test')
    s = 'whole lotta data, whole lotta data, whole lotta data, whole lotta data, whole lotta data'
    data = s.encode()
    p_test.deconstruct_packet(P.create_data_packet(1002,3456,320,104,True,6,data))
    p_test.print_self()
    p_test.set_checksum(0)
    print('')
    p_test.print_self()
    print(p_test.byte_form())
    """
