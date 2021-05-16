import threading
import socket
import sys 
import json 
import time
import udp as pu 
from product import Product
from config import seed
from node import Node
from login import signin


def main():
    #   get port from command line
    port = int(sys.argv[1]) 
    fromA = ("127.0.0.1",port)
    #   login to the market
    name = signin()
    if name != None:    
        print('creating socket and binding socket')
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind((fromA[0],fromA[1]))

        print('creating Node')
        peer = Node()
        # peer.myid = sys.argv[2]
        peer.myid = name
        peer.udp_socket = udp_socket

        print(fromA, peer.myid)

        print('start peer')
        peer.startpeer()
        print('creating thread')
        t1 = threading.Thread(target=peer.rece, args=())
        t2 = threading.Thread(target=peer.send, args=())

        print('start rece and send thread')
        t1.start()
        t2.start()


if __name__ == '__main__':
    main()           

