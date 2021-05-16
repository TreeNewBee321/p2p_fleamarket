import threading
import socket
import sys 
import json 
import time
import udp as pu 
from product import Product
from config import seed



class Node:
    def __init__(self):
        self.seed = seed
        self.peers = {}
        self.myid = ""
        self.udp_socket = {}
        self.product_lst = {}
    #end def


    def load():
        pass
    #end def

    def rece(self):
        while 1:
            data, addr = pu.recembase(self.udp_socket)
            action = json.loads(data)
            print(action["type"])
            if action['type'] == 'newpeer':
                print("A new peer is coming")
                self.peers[action['data']]= addr
                print(addr)
                pu.sendJS(self.udp_socket, addr,{
                "type":'peers',
                "data":self.peers
                })         

            if action['type'] == 'newProduct':
                print('Someone post a new product')
                newProduct = Product(action)
                newProduct.printInfo()
                if newProduct.name in self.product_lst:
                    self.product_lst[newProduct.name].append(newProduct)
                else:
                    self.product_lst[newProduct.name] =  [newProduct]
                #end if

            if action['type'] == 'peers':
                print("Received a bunch of peers")
                self.peers.update(action['data'])
                # introduce youself. 
                pu.broadcastJS(self.udp_socket, {
                    "type":"introduce",
                    "data": self.myid
                },self.peers) 

            if action['type'] == 'introduce':
                print("Get a new friend.")
                self.peers[action['data']]= addr   

            if action['type'] == 'input':
                print(action['data'])  

            if action['type'] == 'exit':
                if(self.myid == action['data']):
                #cannot be closed too fast.  
                    time.sleep(0.5) 
                    break
                    # self.udp_socket.close()
                value, key = self.peers.pop(action['data'])
                print( action['data'] + " is left.") 
                         
    def login(self):
        pass

    def startpeer(self):
        print(f'{self.myid} sending a newpeer')
        print(self.myid)
        print(self.udp_socket)
        pu.sendJS(self.udp_socket, self.seed, {
            "type":"newpeer",
            "data":self.myid
        })

    

    def send(self):

        while 1: 
            msg_input = input("$:")
            if msg_input == "exit":
                pu.broadcastJS(self.udp_socket, {
                    "type":"exit",
                    "data":self.myid
                },self.peers)
                break     
            if msg_input == "friends":
                print(self.peers) 
                continue      
            if msg_input == 'product':
                #TODO
                print('print product infomation here')
                newProduct = Product()
                newProduct.name = input('Your product name: ')
                newProduct.description = input('Please descript your product status:')
                newProduct.price = input('what is the price of the product:')
                newProduct.owner = self.myid
                newProduct.printInfo()
                smsg = newProduct.jsonFile()
                smsg.update({'type': 'newProduct'})
                print(smsg)
                pu.broadcastJS(self.udp_socket, smsg, self.peers)
                continue

            if msg_input == 'products info':
                print('UID\tName\tPrice\tOwner\tDescription')
                for pl_key in self.product_lst:
                    p_lst = self.product_lst[pl_key]
                    for p in p_lst:
                        p.printInfo()
                continue


            l = msg_input.split()
            
            if l[-1] in self.peers.keys():
                toA = self.peers[l[-1]]
                s = ' '.join(l[:-1]) 
                pu.sendJS(self.udp_socket, toA,{
                    "type":"input",
                    "data":s
                })      
            else :
                pu.broadcastJS(self.udp_socket, {
                    "type":"input",
                    "data":msg_input
                },self.peers)
                continue 

#end class
