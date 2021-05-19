import re
import hashlib
import udp as pu 
from product import Product
from config import seed

#   login module
def signin():
    while 1:
        print('Welcome to p2p flea market.\nIf you want to create an account, enter 1.\nIf you want to sign in, enter 2.\nIf you want to leave, enter 3.')
        msg_input = input()
        # create an account
        if msg_input == "1":
            myre = r"^[_a-zA-Z]\w{0,}"
            print("Please enter your account user name:")
            name = input()
            if not re.findall(myre,name):
                print("Username illegal.Please try other username later.")
                continue
            print("Please enter your account password:")
            passwd = input()
            #  check if username is taken
            x = open("account.txt",'a')
            x.close()
            fp = open("account.txt",'r')
            takenFlag = 0

            for line in fp.readlines():
                userInfo = line.strip().split()
                # print(userInfo)
                if len(userInfo) == 0:
                    continue
                if name == userInfo[0]:
                    takenFlag = 1
                    break
            if takenFlag == 1:
                print("The user name is taken.Please try other username later")
                continue

            fp = open("account.txt",'a')
            fp.write(name)
            hl = hashlib.md5()
            hl.update(passwd.encode(encoding='utf-8'))
            fp.write(" ")
            fp.write(hl.hexdigest())
            fp.write("\n")
            print("Successfully create an account.Now login to the flea market.")
            return name
        if msg_input == "2":
            try:
                fp = open("account.txt",'r')
            except:
                print("No account info stores in local host. Please create an account")
                continue
            # ask user to input username and password
            print("Please enter your account user name:")
            name = input()
            print("Please enter your account password:")
            passwd = input()
            # authenticate the user info using the local TXT file 'account.txt'
            for line in fp.readlines():
                userInfo = line.strip().split()
                if name == userInfo[0]:
                    hl = hashlib.md5()
                    hl.update(passwd.encode(encoding='utf-8'))
                    if str(hl.hexdigest()) == userInfo[1]:
                        print("Authentication succeeded.You may now post items in your group.")
                        return name
                else:
                    continue
            print("Authentication failed.Please try again.") 
        if msg_input == "3":
            print("Bye.")
            return None
# end class
