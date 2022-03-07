class Group:

    def __init__(self, netID, name):
        self._netID = netID
        self._name = name

    def get_netID(self):
        return self._netID

    def get_name(self):
        return self._name