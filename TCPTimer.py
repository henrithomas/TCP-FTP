# -*- coding: utf-8 -*-
"""
Henri Thomas
Computer Networks
Assignment 2
"""
class TCPTimer:
    def __init__(self,t):
        self.start_time = 0.0
        self.current_time = 0.0
        self.threshold = t
        self.timeout = False 

    def start_timer(self,start):
        self.start_time = start