import json

class Product:
    def __init__(self, jf=None):
        if jf == None:
            self.uid = None
            self.name = ''
            self.description = ''
            self.price = 0
            self.owner = ''
            self.phone = ''
            self.email = ''
        else:
            self.uid = jf['UID']
            self.name = jf['Name']
            self.description = jf['Description']
            self.price = int(jf['Price'])
            self.owner = jf['Owner']
            self.phone = jf['Phone']
            self.email = jf['Email']
    #end def __init__

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)




    def printInfo(self):
        #print('UID:', self.uid)
        #print('Name:', self.name)
        #print('Price:', self.price)
        #print('Description:', self.description)
        #print('Owner:', self.owner)
        print(f'{self.uid}\t{self.name}\t{self.price}\t{self.owner}\t{self.phone}\t{self.email}\t{self.description}')
    #end def printInfo

    def jsonFile(self):
        return {'UID': self.uid,
                'Name': self.name,
                'Price': self.price,
                'Description': self.description,
                'Phone': self.phone,
                'Email': self.email,
                'Owner': self.owner}
    #end def

    def setAttr(self, attr, value):
        if attr == 'name':
            self.name = value
        elif attr == 'description':
            self.description = value
        elif attr == 'phone':
            self.phone = value
        elif attr == 'price':
            self.price = int(value)
        else:
            self.email = value
    #end def setAttr
#end class
