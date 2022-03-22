class Auditionee:
    '''An object for an Acaprez auditionee'''

    # Will need to figure out exact implementation (what attributes are
    # necessary etc.) 
    def __init__(self, netID, name, class_year, dorm_room,
                 voice_part=None, phone_number=None):
        # Need to add error handling
        self._netID = netID
        self._name = name
        self._class_year = class_year
        self._dorm_room = dorm_room
        self._voice_part = voice_part
        self._phone_number = phone_number
