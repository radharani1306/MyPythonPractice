import socket
import binascii
import struct

__author__='Mullangi Bros'

'''
__headers_support__="""
Ethernet header Extraction
IPv4 header Extraction
Tcp header Extraction
ICMP header Extraction
UDP header Extraction"""
'''
class poori_sniff:
    def __cinit__(self):
        self.data=None


    #    ETH Header Information
    def eth_header(self,data):
        eth_head = data
        eth_head = struct.unpack("!6s6sH", eth_head)
        destination_mac = binascii.hexlify(eth_head[0])
        source_mac = binascii.hexlify(eth_head[1])
        eth_protocol = eth_head[2]
        data = {
            "dmac": destination_mac,
            "smac": source_mac,
            "ethpro": eth_protocol
        }
        return data


    # ICMP Header Information
    def icmp_header(self,data):
        icmp_head = struct.unpack("!BBH", data)
        icmp_type = icmp_head[0]
        icmp_code = icmp_head[1]
        icmp_checksum = icmp_head[2]

        data = {
            "icmptype": icmp_type,
            "icmpcode": icmp_code,
            "icmpchecksum": icmp_checksum
        }
        return data


    # IP Header Information
    def ip_header(self,data):
        ip_head = struct.unpack("!BBHHHBBH4s4s", data)

        _version = ip_head[0]
        _tos = ip_head[1]
        _total_length = ip_head[2]
        _identification = ip_head[3]
        _fragment_Offset = ip_head[4]
        _ttl = ip_head[5]
        _protocol = ip_head[6]
        _header_checksum = ip_head[7]
        _source_address = socket.inet_ntoa(ip_head[8])
        _destination_address = socket.inet_ntoa(ip_head[9])

        data = {
            'Version': _version,
            "Tos": _tos,
            "Total Length": _total_length,
            "Identification": _identification,
            "Fragment": _fragment_Offset,
            "TTL": _ttl,
            "Protocol": _protocol,
            "Header CheckSum": _header_checksum,
            "Source Address": _source_address,
            "Destination Address": _destination_address}
        return data


    #   Tcp Header Information
    def tcp_header(self,data):
        tcp_head = struct.unpack('!HHLLBBHHH', data)

        _source_port = tcp_head[0]
        _destination_port = tcp_head[1]
        _sequence_number = tcp_head[2]
        _acknowledge_number = tcp_head[3]
        _offset_reserved = tcp_head[4]
        _tcp_flag = tcp_head[5]
        _window = tcp_head[6]
        _checksum = tcp_head[7]
        _urgent_pointer = tcp_head[8]

        data = {
            "Source Port": _source_port,
            "Destination Port": _destination_port,
            "Sequence Number": _sequence_number,
            "Acknowledge Number": _acknowledge_number,
            "Offset &amp; Reserved": _offset_reserved,
            "Tcp Flag": _tcp_flag,
            "Window": _window,
            "CheckSum": _checksum,
            "Urgent Pointer": _urgent_pointer}
        return data

    # Mac Address Formating
    def mac_formater(self,a):
        #print("a:: ",a,"   ord(a[0]:: ",a[0])
        b = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x" % (a[0], a[1], a[2], a[3], a[4] , a[5])
        return b

    def get_host(self,q):
        try:
            k=socket.gethostbyaddr(q)
        except:
            k='Unknown'
        return k
