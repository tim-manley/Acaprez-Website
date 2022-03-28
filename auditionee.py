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

    def __str__(self):
        s = ""
        s += f"\nnetID: {self._netID}\n"
        s += f"name: {self._name}\n"
        s += f"class year: {self._class_year}\n"
        s += f"dorm room: {self._dorm_room}\n"
        s += f"voice part(s): {self._voice_part}\n"
        s += f"phone number: {self._phone_number}\n"
        return s
