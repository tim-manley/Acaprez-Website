class Audition:

    def __init__(self, auditionID, auditionee_netID, group_netID, timeslot):
        self._auditionID = auditionID
        self._auditionee_netID = auditionee_netID
        self._group_netID = group_netID
        self._timeslot = timeslot

    def __str__(self):
        # should probably make this better
        s = str(self._auditionID)
        s += " " + str(self._auditionee_netID)
        s += " " + str(self._group_netID)
        s += " " + str(self._timeslot)
        return s

    def to_dict(self):
        '''
        Returns audition object as a dictionary
        '''

        d = dict()

        d['auditionID'] = self._auditionID
        d['auditionee_netID'] = self._auditionee_netID
        d['group_netID'] = self._group_netID
        d['timeslot'] = self._timeslot

        return d
