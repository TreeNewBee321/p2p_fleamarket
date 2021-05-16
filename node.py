import threading
import socket
import sys 
import json 
import time
import hashlib
import os
import pickle
import udp as pu 
from product import Product
from config import seed
from os import path


class Node:
    def __init__(self):
        self.seed = seed
        self.peers = {}
        self.myid = ""
        self.udp_socket = {}
        self.product_lst = {}
    #end def

    def load(self):
        #check file exists
        if path.exists('products'):
            self.product_lst = pickle.load(open('products','rb'))
            print('debug: ', self.product_lst)
        else:
            print('file does not exist, no one post products')
    #end def

    def save(self):
        pickle.dump(self.product_lst, open('products', 'wb')) 
    #end def

    def rece(self):
        while 1:
            data, addr = pu.recembase(self.udp_socket)
            action = json.loads(data)
            print(action["type"])
            if action['type'] == 'newpeer':
                #print("A new peer is coming")
                self.peers[action['data']]= addr
                #print(addr)
                pu.sendJS(self.udp_socket, addr,{
                "type":'peers',
                "data":self.peers
                })         

            if action['type'] == 'newProduct':
                #print('Someone post a new product')
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
                         

    def startpeer(self):
        #print(f'{self.myid} sending a newpeer')
        #print(self.myid)
        #print(self.udp_socket)
        pu.sendJS(self.udp_socket, self.seed, {
            "type":"newpeer",
            "data":self.myid
        })
        self.load()

    def send(self):
        while 1: 
            msg_input = input("$:")
            msg_input = msg_input.strip()
            if msg_input == "exit":
                pu.broadcastJS(self.udp_socket, {
                    "type":"exit",
                    "data":self.myid
                },self.peers)
                self.save()
                break     


            if msg_input == "friends":
                print(self.peers) 
                continue      

            if msg_input == 'product':
                # implement create Product later
                #newProduct = self.createProduct()
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

            if msg_input == 'save':
                self.save()
                continue

            if msg_input == 'products info':
                #   print format here, todo later
                self.printProductInfo()
                continue

            if msg_input == 'update':
                pass

            if msg_input == 'remove':
                self.remove()
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

    #end def sned



    def remove(self):
        p_name = input('Please enter the product you are going to remove: ')
        if p_name in self.product_lst:
            show_lst = []
            p_lst = self.product_lst[p_name]
            uid_lst = [-1]
            for p in p_lst:
                if p.owner == self.myid:
                    show_lst.append(p)
                    uid_lst.append(p.uid)
                #end if
            #end for
            if len(show_lst) == 0:
                print('You did not post any product named', p_name)
            else:
                self.printProductInfo(show_lst)
                uid = int(input('Enter the product UID to remove(-1 to cancel this action): '))
                while uid not in uid_lst:
                    uid = int(input('Invalid UID, please re-enter your product UID(-1 to cancel this action): '))
                #end while
                if uid == -1:
                    print('You cancel this action')
                else:
                    for p in show_lst:
                        if p.uid == uid:
                            p_lst.remove(p)
                            break
                        #endif
                    #end for
                #end if
        else:
            print('there is no such a product named', p_name)
        #end if
        print('Back to main menu')
    #end def

    def createProduct(self):
        p = Product()
        pass
    #end def createProduct(self):

    def printGuide(self):
        print('type \'product\' and enter start to post a product')
        print('type \'products info\' and enter to get product information')
        print('type \'guide\' and enter to print this guide again')

    #end def printGuide()


    def printProductInfo(self, lst=None):
        print('UID\tName\tPrice\tOwner\t\tDescription')
        if lst == None:
            for pl_key in self.product_lst:
                p_lst = self.product_lst[pl_key]
                for p in p_lst:
                    p.printInfo()
                #end for
            #end for
        else: 
            for p in lst:
                p.printInfo()
        #end if 
#end class
