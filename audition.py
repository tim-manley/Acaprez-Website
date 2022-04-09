from calendar import day_abbr


class Audition:

    def __init__(self, auditionID, auditionee_netID, group_netID, 
    timeslot):
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

        d = {}

        d['auditionID'] = self._auditionID
        d['auditionee_netID'] = self._auditionee_netID
        d['group_netID'] = self._group_netID
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
        Returns group netID of given audition
        '''
        return self._group_netID

    def get_timeslot(self):
        '''
        Returns timeslot of given audition
        '''
        return self._timeslot

    def get_formatted_timeslot(self):
        # original: 2022-09-01 17:15:00
        # goal: Sept 1 - 8:30pm
        months = {1:"Jan", 2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
        7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
        
        init_slot = str(self._timeslot)
        datetime = init_slot.split(" ")
        
        ymd = datetime[0].split("-")
        month = int(ymd[1])
        day = int(ymd[2])

        time = datetime[1].split(":")
        hour = int(time[0])
        minute = time[1]
        ampm = "am"

        if (hour >= 12): ampm = "pm"
        hour %= 12

        fin_slot = months[month] + " " + str(day) + " - " + str(hour) + ":" + minute + ampm

        return fin_slot



