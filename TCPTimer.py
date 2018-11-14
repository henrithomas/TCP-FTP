# -*- coding: utf-8 -*-
"""
Henri Thomas
Computer Networks
Assignment 2
"""
import time
import numpy as np
class TCPTimer:
    def __init__(self,t,size):
        self.times = np.zeros(size,dtype = float)
        self.timer_size = size
        self.current_time = 0.0
        self.threshold = t
        self.timeout = False

    def start_new_timer(self):
        for i in range(0,self.timer_size):
            if self.times[i] == 0:
                self.times[i] = time.time()
                break
            
    def shift_times(self):
        for i in range(1,self.timer_size):
            self.times[i-1] = self.times[i]
            if i == self.timer_size - 1:
                self.times[i] = 0.0
            
    def stop_timer(self):
        self.start_time = 0.0
        self.current_time = 0.0
        self.timeout = False

    def check_timeout(self):
        self.current_time = time.time()
        if self.current_time - self.times[0] > self.threshold:
            self.timeout = True
        return self.timeout

if __name__ == "__main__":
    timer = TCPTimer(0.5,3)
    timer.start_new_timer()
    print('times:',timer.times)
    timer.start_new_timer()
    print('times:',timer.times)
    timer.start_new_timer()
    print('times:',timer.times)
    timer.shift_times()
    timer.shift_times()
    print(timer.times)