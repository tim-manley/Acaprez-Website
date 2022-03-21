import os
from psycopg2 import connect
from group import Group

# Database specific variables:
HOST = 'ec2-3-230-238-86.compute-1.amazonaws.com'
DATABASE = 'd8tdd1oslp407c'
USER = 'cmjmzphzaovzef'
PSWD='79e77741d5870f7fd84ac66ddc04c0074e407ba91b548ebd847ee076d8092600'

def get_groups():
    '''
    Returns a list of the groups in the database

        Parameters: 
            None

        Returns: 
            groups ([group]): A list of group objects
    '''
    groups = []

    with connect(host=HOST, database=DATABASE, 
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('SELECT * FROM groups;')
            
            row = cur.fetchone()
            while row is not None:
                # Do we need exception handling???
                group = Group(row[0], row[1])
                groups.append(group)
                row = cur.fetchone()

    return groups

def add_audition(auditionee_netID, group_netID, time_slot):
    '''
    Creates an audition time in the auditionTimes table.

        Parameters:
            auditionee_netID (str): The netID of the auditionee
            group_netID (str)     : The netID of the group
            time_slot (str)       : A date and time in string format, 
                                    the timeslot of the audition.
                                    Format is: "YYYY-MM-DD hh:mm:ss"
                                    24hr time
        
        Returns:
            None
    '''
    with connect(host=HOST, database=DATABASE, 
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''
                        INSERT INTO auditionTimes 
                        (auditioneeNetID, groupNetID, timeslot)
                        VALUES (%s, %s, %s);
                        ''', (auditionee_netID, group_netID, time_slot))

def print_all_auditions():
    '''
    Finish docstring later
    '''
    with connect(host=HOST, database=DATABASE, 
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('SELECT * FROM auditionTimes;')
            
            row = cur.fetchone()
            while row is not None:
                print(row)
                row = cur.fetchone()

# For testing
if __name__ == "__main__":
    add_audition("rjg8", "nassoons", "2022-03-19 19:10:30")
    print_all_auditions()