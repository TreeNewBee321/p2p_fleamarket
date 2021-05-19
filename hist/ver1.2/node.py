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
        self.version = 0
    #end def

    def load(self):
        #check file exists
        if path.exists('products'):
            self.product_lst, self.version = pickle.load(open('products','rb'))
            #print('debug: ', self.product_lst)
        else:
            print('file does not exist, no one post products')
    #end def

    def save(self):
        pickle.dump((self.product_lst, self.version), open('products', 'wb'))
    #end def

    def rece(self):
        while 1:
            data, addr = pu.recembase(self.udp_socket)
            action = json.loads(data)
            if action['type'] == 'newpeer':
                self.peers[action['data']]= addr
                print(self.peers)
                pu.sendJS(self.udp_socket, addr,{
                "type":'peers',
                "data":self.peers
                })         

            if action['type'] == 'newProduct':
                #print('Someone post a new product')
                if action['data'] == self.myid:
                    continue
                newProduct = Product(action)
                #newProduct.printInfo()
                if newProduct.name in self.product_lst:
                    self.product_lst[newProduct.name].append(newProduct)
                else:
                    self.product_lst[newProduct.name] =  [newProduct]
                #end if
                print('debug: sync value is:', action['sync'])
                if not action['sync']:
                    self.version+=1
            #end rec newProduct

            if action['type'] == 'remove':
                if action['data'] == self.myid:
                    continue
                name = action['Name']
                uid = action['UID']
                # Assume the product in list
                if name in self.product_lst:
                    p_lst = self.product_lst[name]
                    for p in p_lst:
                        if p.uid == uid:
                            p_lst.remove(p)
                            print('debug: remove signal, ack')
                            break
                        #end if
                    #end for
                else:
                    pass
                    #print('debug: there is no such a product')
                #end if
                self.version+=1
            #end if action

            if action['type'] == 'update': 
                if action['data'] == self.myid:
                    continue
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
                    pass
                    #print('debug: there is no such a product')
                #end if 
                self.version+=1
            #end if action

            if action['type'] == 'peers':
                self.peers.update(action['data'])
                pu.broadcastJS(self.udp_socket, {
                    "type":"introduce",
                    "data": self.myid,
                },self.peers)
                #   syncchronize dictionary
                for peer in self.peers:
                    if peer == self.myid:
                        continue
                    dist = self.peers[peer]
                    pu.sendJS(self.udp_socket, dist, {
                        "type": "sync",
                        "version": self.version
                        })
                    break
                #end for
            #end rec peers

            if action['type'] == 'sync':
                print('debug: in sync')
                pversion = action['version']
                if pversion > self.version:
                    pu.sendJS(self.udp_socket, addr, {
                        "type": 'broadcast',
                        })
                else:
                    pu.sendJS(self.udp_socket, addr, {'type': 'reset'}) 
                    time.sleep(1)
                    for pn in self.product_lst:
                        p_lst = self.product_lst[pn]
                        for p in p_lst:
                            smsg = p.jsonFile()
                            smsg.update({'type': 'newProduct', 'sync': True, 'data': self.myid})
                            pu.sendJS(self.udp_socket, addr, smsg) 
                        #end for
                    #end for
                    pu.sendJS(self.udp_socket, addr, {'type': 'syncVersion', 'version': self.version})
                #end if
            #end rec sync

            if action['type'] == 'syncVersion':
                self.version = action['version']
            #end rec syncVersion

            if action['type'] == 'broadcast':
                pu.broadcastJS(self.udp_socket, {'type': 'reset'}, self.peers)
                time.sleep(1)
                for pn in self.product_lst:
                    p_lst = self.product_lst[pn]
                    for p in p_lst:
                        smsg = p.jsonFile()
                        smsg.update({'type': 'newProduct', 'sync': True, 'data': self.myid})
                        pu.broadcastJS(self.udp_socket, smsg, self.peers) 
                    #end for
                #end for
                pu.broadcastJS(self.udp_socket, {'type': 'syncVersion', 'version': self.version}, self.peers) 
            #end rec broadcast


            if action['type'] == 'reset':
                self.product_lst.clear()
            #end rec reset

            if action['type'] == 'introduce':
                print('%s is online now' % action['data'])
                self.peers[action['data']]= addr
            #end rec introduce

            if action['type'] == 'input':
                print(action['data'])  

            if action['type'] == 'exit':
                if(self.myid == action['data']):
                #cannot be closed too fast.  
                    time.sleep(0.5) 
                    break
                    # self.udp_socket.close()
                #end if
                print( action['data'] + " is left.") 
                if action['data'] != 'helper':
                    value, key = self.peers.pop(action['data'])
            #end if
        #end while
    #end def
                         

    def startpeer(self):
        pu.sendJS(self.udp_socket, self.seed, {
            "type":"newpeer",
            "data":self.myid
        })
        self.load()
    #end startpeer(self):


    def send(self):
        while 1: 
            msg_input = input("$:")
            msg_input = msg_input.strip()
            if msg_input == "exit":
                if self.myid != 'helper':
                    self.save()
                pu.broadcastJS(self.udp_socket, {
                    "type":"exit",
                    "data":self.myid
                },self.peers)
                break     


            if msg_input == "friends":
                print(self.peers) 
                continue      

            if msg_input == 'product':
                # implement create Product later
                #newProduct = self.createProduct()
                newProduct = Product()
                newProduct.name = input('Your product name: ')
                newProduct.description = input('Please descript your product status: ')
                newProduct.price = float(input('what is the price of the product: '))
                newProduct.phone = input('what is your phone number(enter None to skip this question): ')
                newProduct.email = input('what is your email address: ')
                newProduct.owner = self.myid
                newProduct.uid = self.getUID()
                newProduct.printInfo()
                smsg = newProduct.jsonFile()
                smsg.update({'type': 'newProduct', 'sync': False, 'data': self.myid})
                # add to list
                if newProduct.name in self.product_lst:
                    self.product_lst[newProduct.name].append(newProduct)
                else:
                    self.product_lst[newProduct.name] =  [newProduct]
                print('Product added')
                pu.broadcastJS(self.udp_socket, smsg, self.peers)
                self.version+=1
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
                        "data": self.myid,
                        "Name": p.name,
                        "UID": p.uid,
                        "Attribute": attr,
                        "Value": value}, self.peers)
                else:
                    pass
                    #print('debug: update canceled, nothing happend')
                #end if
                self.version+=1
                continue

            if msg_input == 'remove':
                p = self.remove()
                if p != None:
                    #print('debug: send a remove command to peers')
                    pu.broadcastJS(self.udp_socket, {
                            "type": "remove",
                            "data": self.myid,
                            "Name": p.name,
                            "UID": p.uid}, self.peers)
                else:
                    pass
                    #print('debug: Remove canceled, nothing happened')
                self.version += 1
                continue
            #end remove command 

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
        #end while
        pu.sendJS(self.udp_socket, self.seed, {'type': 'exit', 'data': self.myid})
    #end def send



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
        print("You can use: \n 1. Search by Product Name\n 2. Search by Owner Information\n 3. Show me ALL!\n 4. Quit search")
        search_method = input('Please choose a search method by method Index: ')
        if search_method == "1":
            target_name = input("Please specify a Product Name for searching: ")
            result = self.search_product(target_name)
        if search_method == "2":
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
        if search_method == "3":
            self.printProductInfo()
            # for pl_key in self.product_lst:
            #     for p in self.product_lst[pl_key] :
            #         p.printInfo()
            result = 1
        if search_method == "4":
            self.printProductInfo()
            return None

        if result == 0 :
            print("Sorry there is no Product specified, please try Another Search method")
        
        act = input("If you would like to search again please entering Y, Otherwise quit search by enter N: ")
        if act == "Y" or act == "y" :
            self.search()

        return None

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
                self.printProductInfo(pp_lst)
                # for pp in pp_lst :
                #     pp.printInfo()
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
                    self.printProductInfo(pp_lst)
                    # for pp in pp_lst :
                    #     pp.printInfo()
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
                    self.printProductInfo(pp_lst)
                    # for pp in pp_lst :
                    #     pp.printInfo()
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
                    self.printProductInfo(pp_lst)
                    # for pp in pp_lst :
                    #     pp.printInfo()
                    return 1
        return 0

    def update(self):
        p_name = input('Please enter the product name you are going to update: ')
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
                            attr = input('what infomation are you going to update(name, price, phone, email, description): ')
                            while attr not in attr_lst:
                                attr = input('Invalid input, re-enter your input please(name, price, phone, email, description): ')
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
        print('List version:', self.version) 
        #print('UID\tName\tPrice\tOwner\t\tDescription')
        print('%-20s%-10s%-10s%-15s%-12s%-30s%-50s'%('UID', 'Name', 'Price', 'Owner', 'Phone', 'Email', 'Description'))
        if lst == None:
            for pl_key in self.product_lst:
                p_lst = self.product_lst[pl_key]
                for p in p_lst:
                    #p.printInfo()
                    print('%-20s%-10s%-10f%-15s%-12s%-30s%-50s'%(p.uid, p.name, p.price, p.owner, p.phone, p.email, p.description))
                #end for
            #end for
        else: 
            for p in lst:
                p.printInfo()
        #end if 
#end class
