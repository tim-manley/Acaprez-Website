from typing import List
from psycopg2 import connect
from group import Group
from audition import Audition

#-----------------------------------------------------------------------

# Database specific variables:
HOST = 'ec2-3-230-238-86.compute-1.amazonaws.com'
DATABASE = 'd8tdd1oslp407c'
USER = 'cmjmzphzaovzef'
PSWD='79e77741d5870f7fd84ac66ddc04c0074e407ba91b548ebd847ee076d8092600'

#-----------------------------------------------------------------------

def get_groups() -> List[Group]:
    '''
    Returns a list of the groups in the database

        Parameters: 
            Nothing

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

#-----------------------------------------------------------------------

def add_audition(auditionee_netID: str, 
                 group_netID: str, 
                 time_slot: str):
    '''
    Creates an audition time in the auditionTimes table.

        Parameters:
            auditionee_netID: The netID of the auditionee
            group_netID: The netID of the group
            time_slot: A date and time in string format, the timeslot of 
                       the audition.
                       Format is: "YYYY-MM-DD hh:mm:ss" 24hr time
        
        Returns:
            Nothing
    '''
    # Need to add error handling for timeslot format
    with connect(host=HOST, database=DATABASE, 
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''
                        INSERT INTO auditionTimes 
                        (auditioneeNetID, groupNetID, timeslot)
                        VALUES (%s, %s, %s);
                        ''', (auditionee_netID, group_netID, time_slot))

#-----------------------------------------------------------------------

def get_auditionee_auditions(netID: str) -> List[Audition]:
    '''
    Given an auditionee's netID, returns a list of the auditions they
    are signed up for.

        Parameters:
            netID: The auditionee's netID

        Returns:
            A list of Audition objects, in which are contained the
            details of each audition.
    '''
    auditions = []

    with connect(host=HOST, database=DATABASE, 
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''SELECT * FROM auditionTimes
                           WHERE auditioneeNetID=%s;''', (netID,))
            
            row = cur.fetchone()
            while row is not None:
                # Do we need exception handling???
                audition = Audition(row[0], row[1], row[2], row[3])
                auditions.append(audition)
                row = cur.fetchone()
    
    return auditions

#-----------------------------------------------------------------------

def _print_all_auditions():
    '''
    For testing, prints all the auditions scheduled in the database to 
    the terminal.

        Parameters:
            Nothing

        Returns:
            Nothing
    '''
    with connect(host=HOST, database=DATABASE, 
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('SELECT * FROM auditionTimes;')
            
            row = cur.fetchone()
            while row is not None:
                print(row)
                row = cur.fetchone()

#-----------------------------------------------------------------------

# For testing
if __name__ == "__main__":
    auditions = get_auditionee_auditions('testID')

    for audition in auditions:
        print(audition)
