from datetime import datetime
from multiprocessing.sharedctypes import Value
from operator import add
from os import times
from sys import stderr
from typing import List
from xmlrpc.client import Boolean
from psycopg2 import connect
from group import Group
from audition import Audition
from auditionee import Auditionee

#-----------------------------------------------------------------------

# Database specific variables:
HOST = 'ec2-3-230-238-86.compute-1.amazonaws.com'
DATABASE = 'd8tdd1oslp407c'
USER = 'cmjmzphzaovzef'
PSWD='79e77741d5870f7fd84ac66ddc04c0074e407ba91b548ebd847ee076d8092600'

#-----------------------------------------------------------------------

def get_group(netID: str) -> Group:
    '''
    Returns a list of the groups in the database

        Parameters:
            netID: Net id of the group

        Returns:
            groups ([group]): A list of group objects
    '''

    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''
                        SELECT * FROM groups
                        WHERE netID=%s;
                        ''', (netID,))

            row = cur.fetchone()
            if row is None:
                raise ValueError("No group with given netID")
            
            group = Group(row[0], row[1], row[2])

    return group

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
                group = Group(row[0], row[1], row[2])
                groups.append(group)
                row = cur.fetchone()

    return groups

#-----------------------------------------------------------------------

def get_auditionee(netID: str) -> Auditionee:
    '''
    Given an auditionee's netID, returns an auditionee object containing
    all the auditionee's details.

        Parameters:
            netID: The auditionee's netID

        Returns:
            An auditionee object
    '''
    # Type validation
    if not isinstance(netID, str):
        raise ValueError("netID must be a string")

    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''SELECT * FROM auditionees
                           WHERE netID=%s;''', (netID,))

            row = cur.fetchone()
            # Check the auditionee exists
            if row is None:
                return None
                #raise KeyError(f"No auditionee with {netID} exists")
            
            auditionee = Auditionee(row[0], row[1], row[2], row[3], 
                                    row[5], row[4], row[6])

    return auditionee

#-----------------------------------------------------------------------

def get_group_availability(group_netID: str, aud_netID: str=None) -> List[Audition]:
    '''
    Given a group netID, returns a list of all times that HAVE NOT been
    signed up for by an auditionee.

        Parameters:
        group_netID: The group's netID
        (optional) aud_netID: The auditionee's netID

        Returns:
            A list of Audition objects, in which are contained the 
            details of each un-occupied audition. Returns empty list if
            no auditions are available. Does not return times that the
            auditionee is already signed up for, if provided.
    '''
    if not isinstance(group_netID, str):
        raise ValueError("group_netID must be a string")
    
    available_auditions = []
    
    unavailable = set()
    if aud_netID is not None:
        for aud in get_auditionee_auditions(aud_netID):
            unavailable.add(aud.get_timeslot())

    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''
                        SELECT * FROM auditionTimes
                        WHERE groupNetID=%s 
                        AND auditioneeNetID IS NULL
                        ORDER BY timeSlot
                        ''',
                        (group_netID,))
            
            row = cur.fetchone()
            while row is not None:
                audition = Audition(row[0], row[1], row[2], row[3])
                if row[3] not in unavailable:
                    available_auditions.append(audition)
                row = cur.fetchone()
    
    return available_auditions

#-----------------------------------------------------------------------

def get_group_pending_auditions(group_netID: str) -> List[Audition]:
    '''
    Given a group netID, returns a list of all times that HAVE been
    signed up for by an auditionee and HAVE NOT been offered a callback.

        Parameters:
        group_netID: The group's netID

        Returns:
            A list of Audition objects, in which are contained the 
            details of each audition that has been signed up for.
    '''
    if not isinstance(group_netID, str):
        raise ValueError("group_netID must be a string")
    
    auditions = []

    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''
                        SELECT * FROM auditionTimes
                        WHERE groupNetID=%s 
                        AND auditioneeNetID IS NOT NULL
                        AND callbackOffered=FALSE
                        ORDER BY timeSlot
                        ''',
                        (group_netID,))
            
            row = cur.fetchone()
            while row is not None:
                audition = Audition(row[0], row[1], row[2], row[3])
                auditions.append(audition)
                row = cur.fetchone()
    
    return auditions

#-----------------------------------------------------------------------

def get_group_offered_callbacks(group_netID: str):
    '''
    Given a group netID, returns a list of all times that HAVE been
    signed up for by an auditionee and HAVE been offered a callback.

        Parameters:
        group_netID: The group's netID

        Returns:
            A list of lists of the form [name, acceptance]
    '''
    if not isinstance(group_netID, str):
        raise ValueError("group_netID must be a string")
    
    auditions = []

    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''
                        SELECT * FROM callbackOffers
                        WHERE groupNetID=%s 
                        AND auditioneeNetID IS NOT NULL
                        ''',
                        (group_netID,))
            
            row = cur.fetchone()
            while row is not None:
                if row[2] is True:
                    auditions.append([row[0], "Accepted"])
                else:
                    auditions.append([row[0], "Pending"])
                row = cur.fetchone()
    
    return auditions

#-----------------------------------------------------------------------

def get_group_times(group_netID: str) -> List[Audition]:
    '''
    Given a group netID, returns a list of ALL times that the group 
    has listed for auditions.

        Parameters:
        group_netID: The group's netID

        Returns:
            A list of Audition objects, in which are contained the 
            details of each audition.
    '''
    if not isinstance(group_netID, str):
        raise ValueError("group_netID must be a string")
    
    times = []

    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''
                        SELECT * FROM auditionTimes
                        WHERE groupNetID=%s
                        ORDER BY timeSlot
                        ''',
                        (group_netID,))
            
            row = cur.fetchone()
            while row is not None:
                audition = Audition(row[0], row[1], row[2], row[3])
                times.append(audition)
                row = cur.fetchone()
    
    return times

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
            cur.execute('''
                        SELECT * FROM auditionTimes
                        WHERE auditioneeNetID=%s
                        ORDER BY timeSlot;
                        ''',
                        (netID,))

            row = cur.fetchone()
            while row is not None:
                # Do we need exception handling???
                audition = Audition(row[0], row[1], row[2], row[3])
                auditions.append(audition)
                row = cur.fetchone()

    return auditions

#-----------------------------------------------------------------------

def get_permissions(netID: str):
    """
    Given a netID, returns the permissions of the user.

        Parameters:
            netID: The auditionee's netID

        Returns:
            An string containing the type of user
    """
    # Type validation
    if not isinstance(netID, str):
        raise ValueError("netID must be a string")

    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''SELECT * FROM users
                           WHERE netID=%s;''', (netID,))

            row = cur.fetchone()
            # Check the auditionee exists
            if row is None:
                return None

    return row[1]

#-----------------------------------------------------------------------

def get_audition_dates() -> List[datetime]:
    '''
    Returns the dates that auditions are scheduled for

        Parameters:
            Nothing

        Returns:
            A list of datetimes
    '''
    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''
                        SELECT * FROM auditionDays;
                        ''')
            days = []
            row = cur.fetchone()
            while row is not None:
                days.append(row[0])
                row = cur.fetchone()
            return days

#-----------------------------------------------------------------------

def audition_signup(auditionee_netID: str, group_netID: str,
                 time_slot: str):
    '''
    Adds auditionee to audition time.

        Parameters:
            auditionee_netID: The netID of the auditionee
            group_netID: The netID of the group
            time_slot: A date and time in string format, the timeslot of
                       the audition.
                       Format is: "YYYY-MM-DD hh:mm:ss" 24hr time

        Returns:
            Nothing
    '''
    # Type validation
    if not isinstance(auditionee_netID, str):
        raise ValueError("auditionee_netID must be a string")
    if not isinstance(group_netID, str):
        raise ValueError("group_netID must be a string")
    if not isinstance(time_slot, str):
        raise ValueError("time_slot must be a string")

    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''
                        SELECT * FROM auditionTimes 
                        WHERE groupNetID=%s AND timeSlot=%s;
                        ''',
                        (group_netID, time_slot))
            row = cur.fetchone()
            # Check if audition time exists
            if row is None:
                ex = f"No audition for {group_netID} at {time_slot} "
                ex += "exists"
                raise ValueError(ex)
            # Need to check if someone else is already signed up
            if row[1] is not None:
                ex = f"{row[1]} is already signed up for this audition"
                raise ValueError(ex)

            # Signup the user
            cur.execute('''
                        UPDATE auditionTimes 
                        SET auditioneeNetID=%s
                        WHERE groupNetID=%s AND timeSlot=%s;
                        ''', (auditionee_netID, group_netID, time_slot))

#-----------------------------------------------------------------------

def add_audition_time(group_netID: str, time_slot: str):
    '''
    Creates an available audition time for a group.

        Parameters:
            group_netID: The netID of the group
            time_slot: A date and time in string format, the timeslot of
                       the audition.
                       Format is: "YYYY-MM-DD hh:mm:ss" 24hr time

        Returns:
            Nothing
    '''
    # Type validation
    if not isinstance(group_netID, str):
        raise ValueError("group_netID must be a string")
    if not isinstance(time_slot, str):
        raise ValueError("time_slot must be a string")

    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            # Check the netID is a valid group
            cur.execute('''
                        SELECT * FROM groups
                        WHERE netID=%s;
                        ''',
                        (group_netID,))
            row = cur.fetchone()
            if row is None:
                ex = f"{group_netID} is not a valid group netID"
                raise ValueError(ex)
            # Check if audition time already exists
            cur.execute('''
                        SELECT * FROM auditionTimes 
                        WHERE groupNetID=%s AND timeSlot=%s;
                        ''',
                        (group_netID, time_slot))
            row = cur.fetchone()
            if row is not None:
                ex = f"An audition slot for {group_netID} at "
                ex += f"{time_slot} already exists"
                raise ValueError(ex)

            # Create audition time
            cur.execute('''
                        INSERT INTO auditionTimes 
                        (groupNetID, timeSlot, callbackOffered)
                        VALUES (%s, %s, FALSE);
                        ''', (group_netID, time_slot))

#-----------------------------------------------------------------------

def remove_audition_time(auditionID: int):
    '''
    Given a group and a timeslot, removes the audition time from the
    database.

        Parameters:
            group_netID: The group's netID
            time_slot: The timeslot

        Returns:
            Nothing
    '''
    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            # Check audition time exists
            cur.execute('''SELECT * FROM auditionTimes
                           WHERE auditionID=%s;''', 
                           (auditionID,))
            row = cur.fetchone()
            if row is None:
                raise ValueError("No such audition time exists")
            # Remove audition time from database
            cur.execute('''DELETE FROM auditionTimes
                           WHERE auditionID=%s;''', 
                           (auditionID,))

#-----------------------------------------------------------------------

def add_audition_day(day: str):
    '''
    Given a day, adds it to the auditiondays table

        Parameters:
            day: The day to be added

        Returns:
            Nothing
    '''
    if not isinstance(day, str):
        raise ValueError("time_slot must be a string")

    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''
                        INSERT INTO auditionDays (day)
                        VALUES (%s);
                        ''', (day,))

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

    if access not in ("leader", "auditionee", "admin"):
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

def add_auditionee(netID: str, firstname: str, lastname: str, class_yr: int, dorm: str,
                   voice_pt="", phone=""):
    '''
    Creates an auditionee in the auditionees table.

        Parameters:
            netID: The netID of the auditionee
            firstname: The first name of the auditionee
            lastname: The last name of the auditionee
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
    if not isinstance(firstname, str):
        raise ValueError("first name must be a string")
    if not isinstance(lastname, str):
        raise ValueError("last name must be a string")
    if not isinstance(class_yr, int):
        raise ValueError("class_yr must be an integer")
    if not isinstance(dorm, str):
        raise ValueError("dorm must be a string")
    if not isinstance(voice_pt, str):
        raise ValueError("voice_pt must be a string")
    if not isinstance(phone, str):
        raise ValueError("phone must be a string")

    # Need to add some better validation for inputs here

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
                print(row, flush=True)
                ex = f"An auditionee with netID: {netID} already exists"
                raise ValueError(ex)

            # First need to add to user table with access level of 
            # auditionee
            _add_user(netID, "auditionee")

             # Now add data to auditionees table
            cur.execute('''
                        INSERT INTO auditionees 
                        (netID, firstName, lastName, classYear, 
                         voicePart, dormRoom, phoneNumber)
                        VALUES (%s, %s, %s, %s, %s, %s, %s);
                        ''',
                        (netID, firstname, lastname, class_yr, voice_pt, dorm, phone))

#-----------------------------------------------------------------------

def update_auditionee(netID: str, firstname=None, lastname=None, 
                    class_yr=None, dorm=None, voice_pt=None, phone=None):
    '''
    Updates an auditionee with the given parameters.

        Parameters:
            netID: The netID of the auditionee
            firstname: The first name of the auditionee
            lastname: The last name of the auditionee
            class_yr: The auditionee's class year
            dorm: The auditionee's hall and room number
            voice_pt: The voice part(s) of the auditionee (optional)
            phone: The auditionee's phone number (optional)

        Returns:
            Nothing
    '''
    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            # Check if auditionee exists
            cur.execute('''
                        SELECT * FROM auditionees WHERE netID=%s;
                        ''',
                        (netID,))
            row = cur.fetchone()
            if row is None:
                print(row, flush=True)
                ex = f"No auditionee with netID: {netID} exists"
                raise ValueError(ex)
            # Update table
            if firstname is not None:
                cur.execute('''
                            UPDATE auditionees
                            SET firstName=%s
                            WHERE netID=%s;
                            ''',
                            (firstname, netID))
            if lastname is not None:
                cur.execute('''
                            UPDATE auditionees
                            SET lastName=%s
                            WHERE netID=%s;
                            ''',
                            (lastname, netID))
            if class_yr is not None:
                cur.execute('''
                            UPDATE auditionees
                            SET classYear=%s
                            WHERE netID=%s;
                            ''',
                            (class_yr, netID))
            if dorm is not None:
                cur.execute('''
                            UPDATE auditionees
                            SET dormRoom=%s
                            WHERE netID=%s;
                            ''',
                            (dorm, netID))
            if voice_pt is not None:
                cur.execute('''
                            UPDATE auditionees
                            SET voicePart=%s
                            WHERE netID=%s;
                            ''',
                            (voice_pt, netID))
            if phone is not None:
                cur.execute('''
                            UPDATE auditionees
                            SET phoneNumber=%s
                            WHERE netID=%s;
                            ''',
                            (phone, netID))

#-----------------------------------------------------------------------

def remove_auditionee(netID: str):
    '''
    Given an auditionee's netID, removes the auditionee associated with
    it.

        Parameters:
            netID: The auditionee's netID

        Returns:
            Nothing
    '''
    # Type validation
    if not isinstance(netID, str):
        raise ValueError("netID must be a string")

    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''DELETE FROM auditionees
                           WHERE netID=%s;''', (netID,))
            cur.execute('''
                        DELETE FROM users WHERE netID=%s;
                        ''',
                        (netID,))

#-----------------------------------------------------------------------

def cancel_audition(audition_id: int):
    '''
    Given an audition id, updates the audition so that there is no
    auditionee associated with it, and it is thus available again.

        Parameters:
            audition_id: The audition id
        
        Returns:
            Nothing
    '''
    if not isinstance(audition_id, str):
        raise ValueError("audition_id must be a string")
    
    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            # Check if the audition exists
            cur.execute('''
                        SELECT * FROM auditionTimes
                        WHERE auditionID=%s;
                        ''', (audition_id,))
            row = cur.fetchone()
            if row is None:
                ex = f"No audition with audition_id: {audition_id} "
                ex += "exists"
                raise ValueError(ex)
            # Update the audition
            cur.execute('''
                        UPDATE auditionTimes
                        SET auditioneeNetID = NULL
                        WHERE auditionID=%s;
                        ''', (audition_id,))

#-----------------------------------------------------------------------

def offer_callback(group_netID: str, auditionee_netID: str):
    '''
    Adds an entry to the callbackOffers table for a group to offer a 
    callback to an auditionee, and sets callbackOffered to TRUE for
    the auditionee.

        Parameters:
            group_nedId: the netid of the group offering the callback
            auditionee_netID: the netid of the auditionee being offered
                             a callback.
        
        Returns:
            Nothing
    '''
    if not isinstance(group_netID, str):
        raise ValueError("group_netID should be a string")
    if not isinstance(auditionee_netID, str):
        raise ValueError("auditionee_netID should be a string")

    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            # First check if already in table
            cur.execute('''SELECT * FROM callbackOffers
                           WHERE groupNetID=%s 
                           AND auditioneeNetID=%s;''',
                           (group_netID, auditionee_netID))
            row = cur.fetchone()
            if row is not None:
                ex = f"{auditionee_netID} has already been offered a "
                ex += f"callback by {group_netID}"
                raise ValueError(ex)
            
            # Now add entry to the table, default to not accepted
            cur.execute('''INSERT INTO callbackOffers
                           (auditioneeNetID, groupNetID, accepted)
                           VALUES (%s, %s, FALSE)''',
                           (auditionee_netID, group_netID))
            cur.execute('''UPDATE auditionTimes
                           SET callbackOffered=TRUE
                           WHERE auditioneeNetID=%s
                           AND groupNetID=%s;''',
                           (auditionee_netID, group_netID))

#-----------------------------------------------------------------------

def accept_callback(group_netID: str, auditionee_netID: str):
    '''
    Modifies entry in callbackOffers table with auditionee_netID and 
    group_netID, changing accepted from FALSE to TRUE.

        Parameters:
            group_netID: The group's callback to accept
            auditionee_netID: The netID of the callbackee

        Returns:
            Nothing
    '''
    if not isinstance(group_netID, str):
        raise ValueError("group_netID should be a string")
    if not isinstance(auditionee_netID, str):
        raise ValueError("auditionee_netID should be a string")

    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            # First check if callback offer exists
            cur.execute('''SELECT * FROM callbackOffers
                           WHERE groupNetID=%s 
                           AND auditioneeNetID=%s;''',
                           (group_netID, auditionee_netID))
            row = cur.fetchone()
            if row is None:
                ex = f"{auditionee_netID} has not been offered a "
                ex += f"callback by {group_netID}"
                raise ValueError(ex)
            
            # Now update record to accept callback
            cur.execute('''UPDATE callbackOffers
                           SET accepted=TRUE
                           WHERE groupNetID=%s 
                           AND auditioneeNetID=%s;''',
                           (group_netID, auditionee_netID))


#-----------------------------------------------------------------------

def get_accepted_callbacks(netID: str) -> List[Group]:
    '''
    Given a user's netid, returns a list of all the groups whose
    callbacks they have been offered but HAVE accepted.

        Parameters:
            netID: The netID of the auditionee

        Returns:
            A list of group objects. Empty list if no unnaccepted 
            callbacks.
    '''
    if not isinstance(netID, str):
        raise ValueError("netID should be a string")

    groups = []
    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''SELECT * FROM callbackOffers
                           WHERE auditioneeNetID=%s
                           AND accepted=TRUE;''',
                           (netID,))
            row = cur.fetchone()
            while row is not None:
                group = get_group(row[1])
                groups.append(group)
                row = cur.fetchone()
            return groups

#-----------------------------------------------------------------------

def get_pending_callbacks(netID: str) -> List[Group]:
    '''
    Given a user's netid, returns a list of all the groups whose
    callbacks they have been offered but not yet accepted.

        Parameters:
            netID: The netID of the auditionee

        Returns:
            A list of group objects. Empty list if no unnaccepted 
            callbacks.
    '''
    if not isinstance(netID, str):
        raise ValueError("netID should be a string")

    groups = []
    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''SELECT * FROM callbackOffers
                           WHERE auditioneeNetID=%s
                           AND accepted=FALSE;''',
                           (netID,))
            row = cur.fetchone()
            while row is not None:
                group = get_group(row[1])
                groups.append(group)
                row = cur.fetchone()
            return groups

#-----------------------------------------------------------------------

def get_group_accepted_callbacks(netID: str) -> List[Group]:
    '''
    Given a group's netid, returns a list of all the netIDs whose
    callbacks they have offered and have accepted.

        Parameters:
            netID: The netID of the group

        Returns:
            A list of netIDs. Empty list if no accepted 
            callbacks.
    '''
    if not isinstance(netID, str):
        raise ValueError("netID should be a string")

    auditionees = []
    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''SELECT auditioneeNetID FROM callbackOffers
                           WHERE groupNetID=%s
                           AND accepted=TRUE;''',
                           (netID,))
            row = cur.fetchone()
            while row is not None:
                auditionees.append(row[0])
                row = cur.fetchone()
            return auditionees

#-----------------------------------------------------------------------

def add_callback_session(sessionStart: str):
    '''
    Given a session start time, adds it to the callbackSessions table

        Parameters:
            sessionStart: The start time of the session to be added.

        Returns:
            Nothing
    '''
    if not isinstance(sessionStart, str):
        raise ValueError("sessionStart must be a string")

    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''
                        INSERT INTO callbackSessions (sessionStart)
                        VALUES (%s);
                        ''', (sessionStart,))

#-----------------------------------------------------------------------

def get_callback_sessions() -> List[datetime]:
    '''
    Returns the session times that callbacks are scheduled for

        Parameters:
            Nothing

        Returns:
            A list of datetimes
    '''
    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''
                        SELECT * FROM callbackSessions;
                        ''')
            days = []
            row = cur.fetchone()
            while row is not None:
                days.append(row[0])
                row = cur.fetchone()
            return days

#-----------------------------------------------------------------------

def add_callback_availability(netID: str, timeslot: str):
    '''
    Given an auditionee's netID and a timeslot, adds an entry to the
    callbackAvailability table to indicate the auditionee is available
    at the given time.

        Parameters:
            netID: The auditionee's netID
            timeslot: The timeslot at which they are available

        Returns:
            Nothing
    '''
    if not isinstance(netID, str):
        raise ValueError("netID should be a string")
    if not isinstance(timeslot, str):
        raise ValueError("timeslot should be a string")
    
    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            # Check if auditionee was offered any callbacks
            cur.execute('''
                        SELECT * FROM callbackOffers
                        WHERE auditioneeNetID=%s;
                        ''', (netID,))
            row = cur.fetchone()
            if row is None:
                ex = f"{netID} has not been offered any callbacks"
                raise ValueError(ex)

            # Should check date is one of the callback dates

            # Add entry to availability table
            cur.execute('''
                        INSERT INTO callbackAvailability
                        (auditioneeNetID, timeslot)
                        VALUES (%s, %s);
                        ''', (netID, timeslot))

#-----------------------------------------------------------------------

def get_callback_availability(netID: str) -> List[datetime]:
    '''
    Given an auditionee's netID, returns a list of the times which they
    are available for a callback.
    '''
    if not isinstance(netID, str):
        raise ValueError("netID should be a string")
    
    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            # Check if auditionee was offered any callbacks
            cur.execute('''
                        SELECT * FROM callbackOffers
                        WHERE auditioneeNetID=%s;
                        ''', (netID,))
            row = cur.fetchone()
            if row is None:
                return []
            # Get all the dates they are available
            cur.execute('''SELECT timeslot FROM callbackAvailability
                           WHERE auditioneeNetID=%s''', (netID,))
            times = []
            row = cur.fetchone()
            while row is not None:
                time = row[0]
                times.append(time)
                row = cur.fetchone()
            return times

#-----------------------------------------------------------------------

def schedule_callback(auditioneeID: str, groupID: str, timeslot: str):
    '''
    Given an auditionee's netID and a group's netID, schedules a
    callback at time timeslot by adding an entry in the callbacks table.

        Parameters:
            auditioneeID: The auditionee's netID
            groupID: The group's netID
            timeslot: The callback start time

        Returns:
            Nothing
    '''
    if not isinstance(auditioneeID, str):
        raise ValueError("auditioneeID should be a string")
    if not isinstance(groupID, str):
        raise ValueError("groupID should be a string")
    if not isinstance(timeslot, str):
        raise ValueError("timeslot should be a string")

    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            # Check auditionee has been offered a callback by this group
            cur.execute('''
                        SELECT * FROM callbackOffers
                        WHERE auditioneeNetID=%s
                        AND groupNetID=%s;
                        ''', (auditioneeID, groupID))
            row = cur.fetchone()
            if row is None:
                ex = f"{auditioneeID} was not offered a callback for "
                ex += groupID
                raise ValueError(ex)
            # Check auditionee hasn't already been scheduled for a
            # callback at the same time
            cur.execute('''SELECT * FROM callbacks
                           WHERE auditioneeNetID=%s
                           AND timeslot=%s;''',
                           (auditioneeID, timeslot))
            row = cur.fetchone()
            if row is not None:
                ex = f"{auditioneeID} has already been scheduled a "
                ex += f"callback at {timeslot}"
                raise ValueError(ex)
            # Check auditionee is available at the timeslot
            cur.execute('''SELECT * FROM callbackAvailability
                           WHERE auditioneeNetID=%s
                           AND timeslot=%s;''',
                           (auditioneeID, timeslot))
            row = cur.fetchone()
            if row is None:
                ex = f"{auditioneeID} is not available at {timeslot}"
                raise ValueError(ex)
            # Add entry to callbacks table
            cur.execute('''INSERT INTO callbacks
                           (auditioneeNetID, groupNetID, timeslot)
                           VALUES (%s, %s, %s);''',
                           (auditioneeID, groupID, timeslot))

#-----------------------------------------------------------------------

'''
To test this module, use testdb.py otherwise there is a circular import
if this is the main module.
'''
