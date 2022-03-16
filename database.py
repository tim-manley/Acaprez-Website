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