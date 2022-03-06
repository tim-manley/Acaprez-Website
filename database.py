import os
from psycopg2 import connect
from group import Group

# Database specific variables:
HOST = 'localhost'
DATABASE = 'test_db'
USER = 'tim' # Should use: os.environ['DB_USERNAME']
PASSWORD = 'manley' # Should use: os.environ['DB_PASSWORD']

def get_groups():

    groups = []

    with connect(
        host=HOST,
        database=DATABASE,
        user=USER,
        password=PASSWORD) as con:
        with con.cursor() as cur:
            cur.execute('SELECT * FROM groups;')
            
            row = cur.fetchone()
            while row is not None:
                group = Group(row[0], row[1])
                groups.append(group)
                row = cur.fetchone()

    return groups
