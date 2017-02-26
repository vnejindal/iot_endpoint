"""
This file implements raw socket functionality for sending a packet 

Its functionality is derived from: 
https://sandilands.info/sgordon/teaching/netlab/its332ap5.html
https://csl.name/post/raw-ethernet-frames/
http://www.binarytides.com/raw-socket-programming-in-python-linux/

class rawpacket_v1 is written entirely afresh to cater to exact requirements

Author: Vinay Jindal <vinay.jindal@gmail.com>

"""
import socket 
import binascii
import struct
import sys

class mqtt_packet:
    def __init__(self, topic, payload = None):
        self.topic = topic
        self.payload = payload
        pass
    
    def create_mqtt_packet(self):
        
        PUBLISH = 0x30
        qos = 0
        retain = False
        dup = False
        
        utopic = self.topic.encode('utf-8')
        command = PUBLISH | ((dup&0x1)<<3) | (qos<<1) | retain
        packet = bytearray()
        packet.extend(struct.pack("!B", command))
        
        if payload is None:
            remaining_length = 2+len(utopic)
            #self._easy_log(MQTT_LOG_DEBUG, "Sending PUBLISH (d"+str(dup)+", q"+str(qos)+", r"+str(int(retain))+", m"+str(mid)+", '"+topic+"' (NULL payload)")
        else:
            if isinstance(payload, str):
                upayload = payload.encode('utf-8')
                payloadlen = len(upayload)
            elif isinstance(payload, bytearray):
                payloadlen = len(payload)
            elif isinstance(payload, unicode):
                upayload = payload.encode('utf-8')
                payloadlen = len(upayload)
                
            remaining_length = 2+len(utopic) + payloadlen
        if qos > 0:
            # For message id
            remaining_length = remaining_length + 2
        
        self._pack_remaining_length(packet, remaining_length)
        self._pack_str16(packet, topic)
    
        if qos > 0:
            # For message id
            packet.extend(struct.pack("!H", mid))

        if payload is not None:
            if isinstance(payload, str):
                pack_format = str(payloadlen) + "s"
                packet.extend(struct.pack(pack_format, upayload))
            elif isinstance(payload, bytearray):
                packet.extend(payload)
            elif isinstance(payload, unicode):
                pack_format = str(payloadlen) + "s"
                packet.extend(struct.pack(pack_format, upayload))
            else:
                raise TypeError('payload must be a string, unicode or a bytearray.')
    
        return packet 
    
    def create_sub_packet(self, topic):
       
        SUBSCRIBE = 0x80
        UNSUBSCRIBE = 0xA0
        qos = 0
        dup = False
        
        topics = [(topic.encode('utf-8'), qos)]
        
        remaining_length = 2
        for t in topics:
            remaining_length = remaining_length + 2+len(t[0])+1

        command = SUBSCRIBE | (dup<<3) | (1<<1)
        packet = bytearray()
        packet.extend(struct.pack("!B", command))
        self._pack_remaining_length(packet, remaining_length)
        #local_mid = self._mid_generate()
        local_mid = 1
        packet.extend(struct.pack("!H", local_mid))
        for t in topics:
            self._pack_str16(packet, t[0])
            packet.extend(struct.pack("B", t[1]))
        return packet 
    
    def _pack_remaining_length(self, packet, remaining_length):
        remaining_bytes = []
        while True:
            byte = remaining_length % 128
            remaining_length = remaining_length // 128
            # If there are more digits to encode, set the top bit of this digit
            if remaining_length > 0:
                byte = byte | 0x80

            remaining_bytes.append(byte)
            packet.extend(struct.pack("!B", byte))
            if remaining_length == 0:
                # FIXME - this doesn't deal with incorrectly large payloads
                return packet
    
    def _pack_str16(self, packet, data):
        if sys.version_info[0] < 3:
            if isinstance(data, bytearray):
                packet.extend(struct.pack("!H", len(data)))
                packet.extend(data)
            elif isinstance(data, str):
                udata = data.encode('utf-8')
                pack_format = "!H" + str(len(udata)) + "s"
                packet.extend(struct.pack(pack_format, len(udata), udata))
            elif isinstance(data, unicode):
                udata = data.encode('utf-8')
                pack_format = "!H" + str(len(udata)) + "s"
                packet.extend(struct.pack(pack_format, len(udata), udata))
            else:
                raise TypeError
        else:
            if isinstance(data, bytearray) or isinstance(data, bytes):
                packet.extend(struct.pack("!H", len(data)))
                packet.extend(data)
            elif isinstance(data, str):
                udata = data.encode('utf-8')
                pack_format = "!H" + str(len(udata)) + "s"
                packet.extend(struct.pack(pack_format, len(udata), udata))
            else:
                raise TypeError

class rawpacket:
    """
    Raw packet to be sent on network raw socket
    """
    def __init__(self, payload):
        
        self.payload = payload 
        self.eth_hdr = ''
        self.ip_hdr = ''
        self.tpt_hdr = ''
        
        self._create_ethheader()
        self._create_ipheader()
        self._create_tptheader()
        
    def _create_ethheader(self):
        """
        # Create an Ethernet frame header 
        # - Destination MAC: 6 Bytes 
        # - Source MAC: 6 Bytes 
        # - Type: 2 Bytes (IP = 0x0800) 
        # Change the MAC addresses to match the your computer and the destination 
        """
        self.eth_hdr = [0x00, 0x23, 0x69, 0x3a, 0xf4, 0x7d, # 00:23:69:3A:F4:7D 
            0x90, 0x2b, 0x34, 0x60, 0xdc, 0x2f, # 90:2b:34:60:dc:2f 
            0x08, 0x00]
        
    def _create_ipheader(self):    
        """
        # Create IP datagram header 
        # - Version, header length: 1 Byte (0x45 for normal 20 Byte header) 
        # - DiffServ: 1 Byte (0x00) 
        # - Total length: 2 Bytes 
        # - Identificaiton: 2 Bytes (0x0000) 
        # - Flags, Fragment Offset: 2 Bytes (0x4000 = Don't_Fragment)
        # - Time to Line: 1 Byte (0x40 = 64 hops) 
        # - Protocol: 1 Byte (0x01 = ICMP, 0x06 = TCP, 0x11 = UDP, ...)
        # - Header checksum: 2 Bytes 
        # - Source IP: 4 Bytes 
        # - Destination IP: 4 Bytes 
        """
        self.ip_hdr = [0x45, 
                  0x00, 
                  0x00, 0x54, #Total Length
                  0x80, 0xc6, 
                  0x40, 0x00, 
                  0x40, 
                  0x11,  # Protocol
                  0x36, 0x8a, # checksum - change this! 
                  0x0a, 0xa8, 0x01, 0x07, # 192.168.1.7 
                  0x0a, 0xa8, 0x01, 0x01] # 192.168.1.1 
 
    def _create_tptheader(self):
        """
        Creates Transport Header;
            For UDP Transport 
            - Source Port
            - Destination Port
            - Length 
            - Checksum 
        """
        self.tpt_hdr = [0x15, 0xb3, 
                        0x15, 0xb4,
                        0x00, 0x11,  #Length
                        0x00, 0x00]  #Checksum
    
    def get_packet(self):
        """
        create full packet and returns it 
        Encapsulates it in ethernet header, ip header and transport header
        # Frame structure: 
        # etherent_hdr | ip_hdr | icmp_hdr | icmp_data 
        #    14 B   | 20 B |  16 B  |  48 B 
        """
        eth_hdr_str = "".join(map(chr, self.eth_hdr)) 
        ip_hdr_str = "".join(map(chr, self.ip_hdr)) 
        tpt_hdr_str = "".join(map(chr, self.tpt_hdr))
        
        return eth_hdr_str + ip_hdr_str + tpt_hdr_str + payload
    
   

class rawpacket_v1:
    def __init__(self, smac, dmac, srcip, dstip, sport, dport, payload, proto = 'UDP'):
        
        self.smac = smac
        self.dmac = dmac
        self.srcip = srcip
        self.dstip = dstip
        self.sport = sport 
        self.dport = dport
        self.payload = payload
        self.proto = proto
        if self.proto == 'UDP':
            self.totlen = 12 + 20 + 8 + len(self.payload)
        else:  # In case of TCP or others...assumend only...
            self.totlen = 12 + 20 + 20 + len(self.payload)
	print self.totlen
        
     ######### NEW FUNCTIONS ###########
    def _get_int_to_hex(self, ival, fill = 4):
        """
        Get binary value after filling leading 'fill' zeros
        """
        return binascii.unhexlify(hex(ival)[2:].zfill(fill))
        
    def _get_binary_macaddr(self, macaddr):
        """
        returns binary string representation of macaddr string
        """
        return binascii.unhexlify(''.join(macaddr.split(':')))
    
    def _get_binary_ipaddr(self, ipaddr):
        """
        returns binary ipaddr of string dotted decimal notation 
        """
        return ''.join([self._get_int_to_hex(int(x),2) for x in ipaddr.split('.')])
        #return binascii.unhexlify(''.join(ipaddr.split('.')))
    
    def _get_eth_hdr(self):
        """
        returns binary string representation of ethernet header
         - Destination MAC: 6 Bytes 
         - Source MAC: 6 Bytes 
         - Type: 2 Bytes (IP = 0x0800) 
        """
        smac = self._get_binary_macaddr(self.smac)
        dmac = self._get_binary_macaddr(self.dmac)
        return ''.join([dmac,smac, ''.join(map(chr,[0x08, 0x00]))])

    def _get_ip_hdr(self):
        """
        returns binary representation of ip header
        # Create IP datagram header 
        # - Version, header length: 1 Byte (0x45 for normal 20 Byte header) 
        # - DiffServ: 1 Byte (0x00) 
        # - Total length: 2 Bytes 
        # - Identificaiton: 2 Bytes (0x0000) 
        # - Flags, Fragment Offset: 2 Bytes (0x4000 = Don't_Fragment)
        # - Time to Line: 1 Byte (0x40 = 64 hops) 
        # - Protocol: 1 Byte (0x01 = ICMP, 0x06 = TCP, 0x11 = UDP, ...)
        # - Header checksum: 2 Bytes 
        # - Source IP: 4 Bytes 
        # - Destination IP: 4 Bytes 
        """
        return ''.join([chr(0x45), 
                  chr(0x00), 
                  self._get_int_to_hex(self.totlen),
                  #binascii.unhexlify(hex(self.totlen)[2:].zfill(4)),
                  ''.join(map(chr,[0x80, 0xc6, 
                  0x40, 0x00, 
                  0x40, 
                  0x06,  # Protocol
                  0x00, 0x00])), # checksum - set to 0x00 
                  self._get_binary_ipaddr(self.srcip),
                  self._get_binary_ipaddr(self.dstip)
                  ])
     
    
    def _get_udp_hdr(self):
        """
        Creates Transport Header;
            For UDP Transport 
            - Source Port
            - Destination Port
            - Length 
            - Checksum 
        """
        return ''.join(map(self._get_int_to_hex,[self.sport, 
                        self.dport,
                        self.totlen - 20 - 12, 
                        0x00
                        ]))           
    def _get_tcp_hdr(self):
        """
        creates TCP transport header 
         - Source Port - 2 bytes
         - Destination Port - 2 bytes
         - Sequence Number - 4 bytes 
         - Ack number - 4 bytes 
         - other fields - 4 bytes 
         - checksum - 2 bytes
         - urgent pointer - 2 bytes
         
        
        """
        
        return ''.join(map(self._get_int_to_hex, [self.sport,
                                   self.dport,
                                   0x00,0x01,
                                   0x00,0x00,
                                   0x5018,
                                   0x0805,
                                   0x00, #checksum 
                                   0x00, #urgent pointer                 
                                   ]))
        
    def get_udp_packet(self):
        """
        New version of get packet function 
        """
        eth_hdr = self._get_eth_hdr()
        ip_hdr = self._get_ip_hdr()
        tpt_hdr = self._get_udp_hdr()
        return eth_hdr + ip_hdr + tpt_hdr + self.payload
            
    def get_packet(self):
        """
        New version of get packet function 
        """
        eth_hdr = self._get_eth_hdr()
        ip_hdr = self._get_ip_hdr()
        tpt_hdr = self._get_tcp_hdr()
        return eth_hdr + ip_hdr + tpt_hdr + self.payload
    
    ######### NEW FUNCTIONS ###########
    
class rawsocket:
    """
    Defines class to represent a raw socket and send data to it
    """
    def __init__(self, interface):
        self.interface = interface
        self.protocol = 0 # = ICMP, 6 = TCP, 17 = UDP, etc. 
        # Create a raw socket with address family PACKET 
        self.sock_fd = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
        #Windows: self.sock_fd = socket.socket(socket.AF_INET, socket.SOCK_RAW)
        # Bind the socket to an interface using the specific protocol 
        self.sock_fd.bind((self.interface,self.protocol)) 
 

        
    def send_packet(self, payload):
        """
        sends a raw packet to opened raw socket
        """
        # Convert byte sequences to strings for sending 
        
        self.sock_fd.send(payload) 


payload = 'Hello Vne'
topic = '/hello/state'
mqtt_pkt = mqtt_packet(payload, topic)
pkt = rawpacket_v1('00:0a:ff:12:ff:fe',
                   '00:0a:ff:12:ff:ff',
                   '10.10.10.10',
                   '10.10.10.11',
                   5555,
                   5655,
                   mqtt_pkt.create_sub_packet(topic))
                   #mqtt_pkt.create_mqtt_packet())

rs = rawsocket('lo')
rs.send_packet(pkt.get_packet())
