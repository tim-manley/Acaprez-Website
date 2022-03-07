import os
from psycopg2 import connect
from group import Group

# Database specific variables:
DATABASE_URL = os.environ['DATABASE_URL']

def get_groups():

    groups = []

    with connect(DATABASE_URL, sslmode='require') as con:
        with con.cursor() as cur:
            cur.execute('SELECT * FROM groups;')
            
            row = cur.fetchone()
            while row is not None:
                group = Group(row[0], row[1])
                groups.append(group)
                row = cur.fetchone()

    return groups
