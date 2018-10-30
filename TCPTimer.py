# -*- coding: utf-8 -*-
"""
Henri Thomas
Computer Networks
Assignment 2
"""
import time
class TCPTimer:
    def __init__(self,t):
        self.start_time = 0.0
        self.current_time = 0.0
        self.threshold = t
        self.timeout = False 

    def start_timer(self):
        self.start_time = time.time()
    
    def stop_timer(self):
        self.start_time = 0.0
        self.current_time = 0.0
        self.timeout = False 
        
    def check_timeout(self):
        self.current_time = time.time()
        if self.current_time - self.start_time > self.threshold:
            self.timeout = True
        return self.timeout
    
if __name__ == "__main__":
    timer = TCPTimer(0.5)
    timer.start_timer()
    while not(timer.check_timeout()):
        print('checking time')
    print('timeout')