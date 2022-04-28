import database as db

class Audition:

    def __init__(self, auditionID, auditionee_netID, group_netID, 
    timeslot):
        self._auditionID = auditionID
        self._auditionee_netID = auditionee_netID
        self._group_netID = group_netID
        self._timeslot = timeslot
        # self._group is only set from the auditionee page (where it is
        # needed)

    def __str__(self):
        # should probably make this better
        s = str(self._auditionID)
        s += " " + str(self._auditionee_netID)
        s += " " + str(self._group_netID)
        s += " " + str(self._group)
        s += " " + str(self._timeslot)
        return s

    def to_dict(self):
        '''
        Returns audition object as a dictionary
        '''

        d = {}

        d['auditionID'] = self._auditionID
        d['auditionee_netID'] = self._auditionee_netID
        d['group'] = self._group_netID
        d['group_name'] = self._group_name
        d['timeslot'] = self._timeslot

        return d

    def get_auditionID(self):
        '''
        Returns auditionID of given audition
        '''
        return self._auditionID

    def get_auditionee_netID(self):
        '''
        Returns auditionee netID of given audition
        '''
        return self._auditionee_netID

    def get_group(self):
        '''
        Returns group netID for a given audition
        '''
        return self._group_netID
    
    def get_group_name(self):
        '''
        Returns group name for a given audition
        '''
        return self._group.get_name()

    def get_group_url(self):
        '''
        Returns group url for a given audition
        '''
        return self._group.get_url()

    def get_timeslot(self):
        '''
        Returns timeslot of given audition
        '''
        return self._timeslot

    def get_formatted_timeslot(self):
        # original: 2022-09-01 17:15:00
        # goal: Sept 1 - 8:30pm

        return self._timeslot.strftime("%b %-d - %-I:%M %p")

    def set_group(self):
        self._group = db.get_group(self._group_netID)
