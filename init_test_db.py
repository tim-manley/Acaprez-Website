'''
Created this file based on the tutorial provided at:
https://www.digitalocean.com/community/tutorials/how-to-use-a-postgresql-database-in-a-flask-application
'''

import os
from psycopg2 import connect

# Database specific variables:
HOST = 'localhost'
DATABASE = 'test_db'
USER = 'tim' # Should use: os.environ['DB_USERNAME']
PASSWORD = 'manley' # Should use: os.environ['DB_PASSWORD']

def main():
    # Setup connection and cursor
    with connect(host=HOST, database=DATABASE, 
                 user=USER, password=PASSWORD) as con:
        with con.cursor() as cur:
            # Create the table
            cur.execute('DROP TABLE IF EXISTS groups;')
            cur.execute('''CREATE TABLE groups 
                         (netID varchar(50) PRIMARY KEY,
                          name varchar(150) NOT NULL);''')
            # Insert data into table
            cur.execute('''INSERT INTO groups (netID, name)
                           VALUES (%s, %s)''',
                           ('nassoons', 'The Princeton Nassoons'))
            cur.execute('''INSERT INTO groups (netID, name)
                           VALUES (%s, %s)''',
                           ('footnotes', 'The Princeton Footnotes'))
            # Commit changes
            con.commit()


if __name__ == '__main__':
    main()