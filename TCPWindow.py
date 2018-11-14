# -*- coding: utf-8 -*-
"""
Henri Thomas
Computer Networks
Assignment 2
"""
import numpy as np
from bitstring import BitArray
from bitstring import Bits
#add a window shift function
class TCPWindow:
    def __init__(self,start,size,seq_size):
        self.file_offset = 0
        self.initial_base = start
        self.base = start
        self.next_sequence_number = 0
        self.window_size = size
        self.sequence_size = seq_size
        self.sequence_array = np.zeros(size,dtype = int)
        self.ack_array = BitArray(int = 0,length=size)
        self.full = False

    def set_base(self,b):
        self.base = b

    def set_file_offset(self,offset):
        self.file_offset = offset

    def get_base(self):
        return self.base

    def get_file_offset(self):
        return self.file_offset

    def update_window(self,seq):
        for i in range(0,self.window_size):
            if self.sequence_array[i] == 0:
                if i == (self.window_size - 1):
                    self.sequence_array[i] = seq
                    self.full = True
                elif i == 0:
                    self.sequence_array[i] = seq
                    self.next_sequence_number = seq + self.sequence_size
                    self.base = seq
                    self.file_offset = seq - self.initial_base
                else:
                    self.sequence_array[i] = seq
                    self.next_sequence_number = seq + self.sequence_size
                break

    def shift_window(self):
        for i in range(1,self.window_size):     
            self.sequence_array[i-1] = self.sequence_array[i]
            if i == self.window_size - 1:
                self.sequence_array[i] = 0
        self.full = False
        
    def update_ack(self,i,ack):
        self.full = False
        self.ack_array.set(i,ack)

    def print_self(self):
        print('window file offset:',self.file_offset)
        print('window base:',self.base)
        print('window size:',self.window_size)
        print('window sequence array:',self.sequence_array)
        print('window ack array:',self.ack_array.bin)
        print('window full:',self.full)
        print('window sequence size:',self.sequence_size)
        print('window next sequence number:',self.next_sequence_number)

if __name__ == "__main__":
    window = TCPWindow(302,4,100)
    window.print_self()
    window.set_file_offset(512)
    window.set_base(302)
    window.update_window(302)
    window.update_window(402)
    window.update_window(502)
    window.update_window(602)
    #window.update_ack(1,True)
    window.print_self()
    window.shift_window()
    window.print_self()
    window.shift_window()
    window.print_self()