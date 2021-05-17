import threading
import socket
import sys 
import json 
import time
import hashlib
import os
import pickle
import udp as pu 
from datetime import timezone
import datetime
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
            #print('debug: ', self.product_lst)
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

            if action['type'] == 'remove':
                name = action['Name']
                uid = action['UID']
                # Assume the product in list
                if name in self.product_lst:
                    p_lst = self.product_lst[name]
                    for p in p_lst:
                        if p.uid == uid:
                            p_lst.remove(p)
                            #print('debug: remove signal, ack')
                            break
                        #end if
                    #end for
                else:
                    #print('debug: there is no such a product')
                #end if
            #end if action

            if action['type'] == 'update': 
                name = action['Name']
                uid = action['UID']
                attr = action['Attribute']
                value = action['Value']
                # Assume the product in list
                if name in self.product_lst:
                    p_lst = self.product_lst[name]
                    for p in p_lst:
                        if p.uid == uid:
                            p.setAttr(attr,value)
                            #print('debug: update signal, ack')
                            break
                        #end if
                    #end for
                else:
                    #print('debug: there is no such a product')
                #end if 
            #end if action

            

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
            #end if
        #end while
    #end def
                         

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
                newProduct.uid = self.getUID()
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
                p, attr, value = self.update()
                if p != None:
                    #print('debug: send a update command to peers')
                    pu.broadcastJS(self.udp_socket, {
                        "type": "update",
                        "Name": p.name,
                        "UID": p.uid,
                        "Attribute": attr,
                        "Value": value}, self.peers)
                else:
                    #print('debug: update canceled, nothing happend')
                #end if
                continue

            if msg_input == 'remove':
                p = self.remove()
                if p != None:
                    #print('debug: send a remove command to peers')
                    pu.broadcastJS(self.udp_socket, {
                            "type": "remove",
                            "Name": p.name,
                            "UID": p.uid}, self.peers)
                else:
                    #print('debug: Remove canceled, nothing happened')
                continue

            if msg_input == 'search':
                self.search()
                continue

            if msg_input == 'guide':
                self.printGuide()
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
            uid_lst = ['-1']
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
                uid = input('Enter the product UID to remove(-1 to cancel this action): ')
                while uid not in uid_lst:
                    uid = input('Invalid UID, please re-enter your product UID(-1 to cancel this action): ')
                #end while
                if uid == '-1':
                    print('You cancel this action')
                else:
                    for p in show_lst:
                        if p.uid == uid:
                            p_lst.remove(p)
                            print('Remove successfully')
                            return p
                            break
                        #endif
                    #end for
                #end if
        else:
            print('there is no such a product named', p_name)
        #end if
        print('Back to main menu')
        return None
    #end def

    def search(self):
        category_num = 0
        total_p_num = 0
        result = 0
        for pl_key in self.product_lst:
            category_num += 1
            total_p_num += len(self.product_lst[pl_key])
        
        print("now there are {} category and totally {} product in this community".format(category_num, total_p_num))
        print("You can use: \n 1. Search by Category Name\n 2. Search by Product Name\n 3. Search by Owner Information\n 4. Show me ALL!\n 5. Quit search")
        search_method = input('Please choose a search method by method Index: ')
        if search_method == "1":
            target_name = input("Please specify a Category Name for searching: ")
            result = self.search_category(target_name)
        if search_method == "2":
            target_name = input("Please specify a Product Name for searching: ")
            result = self.search_product(target_name)
        if search_method == "3":
            print("There are three types of user info: \n 1. Search by Owner Name\n 2. Search by Owner phone number\n 3. Search by Owner email\n ")
            target_type = input("Please specify a Owner Information type for search by type index: ")
            if target_type == "1":
                target_info = input("Please specify the owner name: ")
                result = self.search_owner(target_info, "", "")
            if target_type == "2":
                target_info = input("Please specify the owner phone number: ")
                result = self.search_owner("", target_info, "")
            if target_type == "3":
                target_info = input("Please specify the owner email address: ")
                result = self.search_owner("", "", target_info)
        if search_method == "4":
            for pl_key in self.product_lst:
                for p in self.product_lst[pl_key] :
                    p.printInfo()
            result = 1
        if search_method == "5":
            return None

        if result == 0 :
            print("Sorry there is no Product specified, please try Another Search method")
        
        act = input("If you would like to search again please entering Y, Otherwise quit search by enter N: ")
        if act == "Y" or act == "y" :
            self.search()

        return None

    def search_category(self, target_name) :
        for pl_key in self.product_lst:
            if (target_name == pl_key) :
                print("Found the Category: {}".format(target_name))
                print("Here are the products under this category: ")
                for prod in self.product_lst[pl_key] :
                    prod.printInfo()
                return 1
        return 0

    def search_product(self, target_name) :
        pp_lst = []
        for pl_key in self.product_lst:
            p_lst = self.product_lst[pl_key]
            for p in p_lst :
                if p.name == target_name:
                    pp_lst.append(p)
            if len(pp_lst)>0 :
                print("Found the Product with name: {}".format(target_name))
                print("Here are the products : ")
                for pp in pp_lst :
                    pp.printInfo()
                return 1
        return 0

    def search_owner(self, owner_name="", owner_phone="", owner_email="") :
        if len(owner_name)>0 :
            pp_lst = []
            for pl_key in self.product_lst:
                p_lst = self.product_lst[pl_key]
                for p in p_lst :
                    if p.owner == owner_name:
                        pp_lst.append(p)
                if len(pp_lst)>0 :
                    print("Found the Product with owner name: {}".format(owner_name))
                    print("Here are the products : ")
                    for pp in pp_lst :
                        pp.printInfo()
                    return 1
        if len(owner_phone)>0 :
            pp_lst = []
            for pl_key in self.product_lst:
                p_lst = self.product_lst[pl_key]
                for p in p_lst :
                    if p.phone == owner_phone:
                        pp_lst.append(p)
                if len(pp_lst)>0 :
                    print("Found the Product with owner phone number: {}".format(owner_phone))
                    print("Here are the products : ")
                    for pp in pp_lst :
                        pp.printInfo()
                    return 1
        if len(owner_email)>0 :
            pp_lst = []
            for pl_key in self.product_lst:
                p_lst = self.product_lst[pl_key]
                for p in p_lst :
                    if p.email == owner_email:
                        pp_lst.append(p)
                if len(pp_lst)>0 :
                    print("Found the Product with owner email address: {}".format(owner_email))
                    print("Here are the products : ")
                    for pp in pp_lst :
                        pp.printInfo()
                    return 1
        return 0

    def update(self):
        p_name = input('Please enter the product you are going to update: ')
        if p_name in self.product_lst:
            show_lst = []
            p_lst = self.product_lst[p_name]
            uid_lst = ['-1']

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
                uid = input('Enter the product UID to update(-1 to cancel this action): ')
                while uid not in uid_lst:
                    uid = input('Invalid UID, please re-enter your product UID(-1 to cancel this action): ')
                #end while
                if uid == '-1':
                    print('You cancel this action')
                else:
                    for p in show_lst:
                        if p.uid == uid:
                            attr_lst = ['name', 'phone', 'description', 'price', 'email']
                            attr = input('what infomation are you going to update? ')
                            while attr not in attr_lst:
                                attr = input('Invalid input, re-enter your input please(name, description, price, phone, email): ')
                            #end while
                            value = input(f'enter your new {attr}:')
                            p.setAttr(attr, value)
                            return p, attr, value
                        #endif
                    #end for
                #end if
        else:
            print('there is no such a product named', p_name)
        #end if
        print('Back to main menu')

        return None, '', ''
    #end def update

    def createProduct(self):
        p = Product()
        pass
    #end def createProduct(self):

    def printGuide(self):
        print('type \'product\' and press enter to post a product')
        print('type \'products info\' and press enter to get product information')
        print('type \'remove\' and press enter to remove the product that you posted')
        print('type \'update\' and press enter to update a product that you posted')
        print('type \'search\' and press enter to start a search for a product')
        print('type \'guide\' and press enter to print this guide again')
        print('type \'exit\' and press enter to stop this program at any time you want to leave')

    #end def printGuide()


    def getUID(self):
        dt = datetime.datetime.now(timezone.utc)
        utc_time = dt.replace(tzinfo=timezone.utc)
        date, prefix = str(utc_time).split('.')
        date = date[4:].replace('-', '')
        date = date.replace(':', '')
        date = date.replace(' ', '')
        uid = date + prefix[:1]
        return uid

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
