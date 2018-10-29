# -*- coding: utf-8 -*-
"""
Henri Thomas
Computer Networks
Assignment 2
"""
import numpy as np
from bitstring import BitArray
from bitstring import Bits
class TCPWindow:
    def __init__(self,start,size):
        self.file_offset = 0
        self.base = start
        self.window_size = size
        self.sequence_array = np.zeros(size,dtype = int)
        self.ack_array = BitArray(int = 0,length=size)
    
    def set_base(self,b):
        self.base = b
        
    def set_file_offset(self,offset):
        self.file_offset = offset
        
    def get_base(self):
        return self.base
    
    def get_file_offset(self):
        return self.file_offset
    
    def update_window(self,i,seq):
        self.sequence_array[i] = seq
        
    def update_ack(self,i,ack):
        self.ack_array.set(i,ack)
        
    def print_self(self):
        print('window file offset:',self.file_offset)
        print('window base:',self.base)
        print('window size:',self.window_size)
        print('window sequence array:',self.sequence_array)
        print('window ack array:',self.ack_array.bin)
    
if __name__ == "__main__":
    window = TCPWindow(301,4)
    window.print_self()
    window.set_file_offset(512)
    window.set_base(302)
    window.update_window(0,400)
    window.update_window(1,500)
    window.update_window(2,600)
    window.update_ack(1,True)
    window.print_self()