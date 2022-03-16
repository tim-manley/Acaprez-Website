class Group:
    '''An object representing an Acaprez acapella group'''

    def __init__(self, netID, name):
        if netID is None:
            raise ValueError("netID must contain a value")
        if name is None:
            raise ValueError("name must contain a value")

        self._netID = netID
        self._name = name

    def get_netID(self):
        '''Returns the netID of the group'''
        return self._netID

    def get_name(self):
        '''Returns the name of the group'''
        return self._name