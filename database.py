from typing import List
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
            
            auditionee = Auditionee(row[0], row[1], row[2], row[4], 
                                    row[3], row[5])

    return auditionee

#-----------------------------------------------------------------------

def get_group_availability(group_netID: str) -> List[Audition]:
    '''
    Given a group netID, returns a list of all times that HAVE NOT been
    signed up for by an auditionee.

        Parameters:
        group_netID: The group's netID

        Returns:
            A list of Audition objects, in which are contained the 
            details of each un-occupied audition. Returns empty list if
            no auditions are available
    '''
    if not isinstance(group_netID, str):
        raise ValueError("group_netID must be a string")
    
    available_auditions = []

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
                available_auditions.append(audition)
                row = cur.fetchone()
    
    return available_auditions

#-----------------------------------------------------------------------

def get_group_auditions(group_netID: str) -> List[Audition]:
    '''
    Given a group netID, returns a list of all times that HAVE been
    signed up for by an auditionee.

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
                        INSERT INTO auditionTimes (groupNetID, timeSlot)
                        VALUES (%s, %s);
                        ''', (group_netID, time_slot))

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
                        (netID, name, classYear, 
                         voicePart, dormRoom, phoneNumber)
                        VALUES (%s, %s, %s, %s, %s, %s);
                        ''',
                        (netID, name, class_yr, voice_pt, dorm, phone))

#-----------------------------------------------------------------------

def update_auditionee(netID: str, name=None, class_yr=None, dorm=None,
                      voice_pt=None, phone=None):
    '''
    Updates an auditionee with the given parameters.

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
            if name is not None:
                cur.execute('''
                            UPDATE auditionees
                            SET name=%s
                            WHERE netID=%s;
                            ''',
                            (name, netID))
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

def _print_all_auditionees():
    '''
    For testing, prints all the auditionees in the database

        Parameters:
            Nothing

        Returns:
            Nothing
    '''
    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('SELECT * FROM auditionees;')
            
            row = cur.fetchone()
            while row is not None:
                print(row, flush=True)
                row = cur.fetchone()
            

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

def _print_all_users():
    '''
    For testing, prints all the users scheduled in the database to
    the terminal.

        Parameters:
            Nothing

        Returns:
            Nothing
    '''
    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('SELECT * FROM users;')
            
            row = cur.fetchone()
            while row is not None:
                print(row)
                row = cur.fetchone()


#-----------------------------------------------------------------------

# For testing
if __name__ == "__main__":
    update_auditionee("tdmanley", "Tim Manley", 2023, "Spelman",
    "Tenor", "0987654321")
