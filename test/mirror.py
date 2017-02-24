"""
Implements the packet mirroring functionality 
"""
from Queue import Queue
from threading import Thread
import socket

from time import sleep


class packetMirror:
    """This is a class that implements packet mirroring
    """
    def __init__(self, ipaddr, port, interface = None, start = False):
        print 'Mirroring object created'
        self.ipaddr = ipaddr
        self.port = port 
        self.interface = interface 
        self.start = start
        self.msgq = Queue()
        print 'starting thread'
        try:
            self.thread_id = Thread(target=self.thread_start, args=(self.start,))
            self.thread_id.start()
        except Exception: 
            print 'error occured'
        self.sock = -1
        
    def put_msg(self, packet):
        """
        Put a packet in queue
        """
        if self.start is True: 
            self.msgq.put(packet)
    
    def get_msg(self):
        """
        Reads a message from queue
        """
        return self.msgq.get()
        
    def process_queue(self):
        """
        Starts reading the messages from queue 
        """
        while True:
            msg = self.get_msg()
            print 'msg received: ', msg
            self.process_message(msg)
            self.msgq.task_done()
        
    def process_message(self, msg):
        """
        Processes messages received in queue
        """
        print 'sent:', msg, self.ipaddr, self.port
        self.sock.sendto(msg,(self.ipaddr, self.port))
        pass
    
    def start_capture(self):
        self.start = True
    
    def stop_capture(self):
        self.start = False
    
    def thread_start(self, start):
        """
        starts the queue thread 
        """
        print 'thread started'
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('192.168.1.39', 18888))
        self.process_queue()
         
    def __str__(self):        
        ret_str = 'ip = %s:%d itf=%s qsize=%d' % (self.ipaddr, self.port, self.interface, self.msgq.qsize())
        return ret_str
        
    def log_packetmirror_stats(self):
        """
        Prints packet mirroring statistics
        """
        print self
        

ipaddr, port = '192.168.1.49', 18888
pkt_obj = packetMirror(ipaddr, port)

pkt_obj.start_capture()

while True:
    packet = 'ABCD'
    print 'sending packets'
    pkt_obj.put_msg(packet)
    print pkt_obj
    sleep(1)

