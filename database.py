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

def add_audition(auditionee_netID: str, group_netID: str, 
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
    # Need to add error handling for arguments

    with connect(host=HOST, database=DATABASE, 
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''
                        INSERT INTO auditionTimes 
                        (auditioneeNetID, groupNetID, timeslot)
                        VALUES (%s, %s, %s);
                        ''', (auditionee_netID, group_netID, time_slot))

#-----------------------------------------------------------------------

def _add_user(netID: str, access: str):
    '''
    File private method which adds a user to the users table. Should
    only be called from within add_auditionee, add_group or add_admin.

        Parameters:
            netID: The netID of the user
            access: The access level of the user. The access levels are:
                    ("leader", "auditionee", "admin")

        Returns:
            Nothing
    '''
    if not isinstance(netID, str):
        raise ValueError("netID must be a string")
    if not isinstance(access, str):
        raise ValueError("access must be a string")

    if access != "leader" and access != "auditionee" and access != "admin":
        err_str = "access must be one of \"leader\", \"auditionee\" or "
        err_str += "\"admin\""
        raise ValueError(err_str)

    with connect(host=HOST, database=DATABASE, 
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            # Check if user is already in the table
            cur.execute('''
                        SELECT * FROM users WHERE netID=%s;
                        ''',
                        (netID,))
            row = cur.fetchone()
            if row is not None:
                ex = f"A user with netID: \"{netID}\" already exists"
                raise ValueError(ex)

            # Add the user
            cur.execute('''
                        INSERT INTO users 
                        (netID, access)
                        VALUES (%s, %s);
                        ''', (netID, access))

#-----------------------------------------------------------------------

def add_auditionee(netID: str, name: str, class_yr: int, dorm: str, 
                   voice_pt="", phone=""):
    '''
    Creates an auditionee in the auditionees table.

        Parameters:
            netID: The netID of the auditionee
            name: The name of the auditionee
            class_yr: The auditionee's class year
            dorm: The auditionee's hall and room number
            voice_pt: The voice part(s) of the auditionee (optional)
            phone: The auditionee's phone number (optional)

        Returns:
            Nothing
    '''
    # Check argument types
    if not isinstance(netID, str):
        raise ValueError("netID must be a string")
    if not isinstance(name, str):
        raise ValueError("name must be a string")
    if not isinstance(class_yr, int):
        raise ValueError("class_yr must be an integer")
    if not isinstance(dorm, str):
        raise ValueError("dorm must be a string")
    if not isinstance(voice_pt, str):
        raise ValueError("voice_pt must be a string")
    if not isinstance(phone, str):
        raise ValueError("phone must be a string")

    with connect(host=HOST, database=DATABASE, 
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            # Check if auditionee is already in the table
            cur.execute('''
                        SELECT * FROM auditionees WHERE netID=%s;
                        ''',
                        (netID,))
            row = cur.fetchone()
            if row is not None:
                ex = f"An auditionee with netID: {netID} already exists"
                raise ValueError(ex)
            
            # First need to add to user table with access level of auditionee
            _add_user(netID, "Auditionee")

             # Now add data to auditionees table
            cur.execute('''
                        INSERT INTO auditionees 
                        (netID, name, classYear, 
                         voicePart, dormRoom, phoneNumber)
                        VALUES (%s, %s, %d, %s, %s, %s);
                        ''', 
                        (netID, name, class_yr, voice_pt, dorm, phone))

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
    userID = "testUser"

    try:
        _add_user(5, 5)
    except Exception as ex:
        print(ex)
    try:
        _add_user(userID, 5)
    except Exception as ex:
        print(ex)
    try:
        _add_user(userID, "wrong_access")
    except Exception as ex:
        print(ex)
    try:
        _add_user(userID, "leader")
    except Exception as ex:
        print(ex)
    try:
        _add_user(userID, "admin")
    except Exception as ex:
        print(ex)
