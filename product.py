
class Product:
    def __init__(self, jf=None):
        if jf == None:
            self.uid = None
            self.name = ''
            self.description = ''
            self.price = 0
            self.owner = ''
        else:
            self.uid = jf['UID']
            self.name = jf['Name']
            self.description = jf['Description']
            self.price = int(jf['Price'])
            self.owner = jf['Owner']
    #end def __init__





    def printInfo(self):
        #print('UID:', self.uid)
        #print('Name:', self.name)
        #print('Price:', self.price)
        #print('Description:', self.description)
        #print('Owner:', self.owner)
        print(f'{self.uid}\t{self.name}\t{self.price}\t{self.owner}\t{self.description}')
    #end def printInfo

    def jsonFile(self):
        return {'UID': self.uid,
                'Name': self.name,
                'Price': self.price,
                'Description': self.description,
                'Owner': self.owner}

#end class
