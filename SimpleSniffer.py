import socket
import binascii
import struct
import os
import my_sniff as ms

print ("Author:: ",ms.__author__)

# if operating system is windows
if os.name == "nt":
    s = socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.IPPROTO_IP)
    s.bind(("192.168.81.1",0))
    s.setsockopt(socket.IPPROTO_IP,socket.IP_HDRINCL,1)
    s.ioctl(socket.SIO_RCVALL,socket.RCVALL_ON)
    print("In Windows OS")
# if operating system is linux
else:
    s=socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0800))
    print("In Non-Windows OS")


# create loop
while True:

    # Capture packets from network
    pkt=s.recvfrom(65565)

    # extract packets with the help of pye.unpack class
    poori_pack=ms.poori_sniff()

    print ("\n\n===&gt;&gt; [+] ------------ Ethernet Header----- [+]")

    # print data on terminal
    temp = poori_pack.eth_header(pkt[0][0:14])
    for key in temp:
        if(key.find("mac") != -1):
           print("{} : {} | ".format(key, poori_pack.mac_formater(temp[key])))
        else:
           print ("{} : {} | ".format(key,temp[key]))

    print ("\n===&gt;&gt; [+] ------------ IP Header ------------[+]")
    temp = poori_pack.ip_header(pkt[0][14:34])
    for key in temp:
        print ("{} : {} | ".format(key,temp[key]))
        
    print ("\n===&gt;&gt; [+] ------------ Tcp Header ----------- [+]")
    temp = poori_pack.tcp_header(pkt[0][34:54])
    for  key in temp:
        print ("{} : {} | ".format(key,temp[key]))


