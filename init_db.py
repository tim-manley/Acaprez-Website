'''
Created this file based on the tutorial provided at:
https://www.digitalocean.com/community/tutorials/how-to-use-a-postgresql-database-in-a-flask-application
'''

import os
from psycopg2 import connect

# Database specific variables:
HOST = 'ec2-3-230-238-86.compute-1.amazonaws.com'
DATABASE = 'd8tdd1oslp407c'
USER = 'cmjmzphzaovzef'
PSWD='79e77741d5870f7fd84ac66ddc04c0074e407ba91b548ebd847ee076d8092600'


def create_users(cur):
    cur.execute('''CREATE TABLE  IF NOT EXISTS users 
                    (netID varchar(50) PRIMARY KEY,
                     access varchar(50) NOT NULL);''')

def add_user(cur, netID, access):
    cur.execute('''INSERT INTO users (netID, access)
                   VALUES (%s, %s);''',
                   (netID, access))

def create_groups(cur):
    cur.execute('DROP TABLE IF EXISTS groups;')
    cur.execute('''CREATE TABLE groups 
                    (netID varchar(50) PRIMARY KEY,
                    name varchar(50) NOT NULL);''')

def add_group(cur, netID, name):
    add_user(cur, netID, 'leader')
    cur.execute('''INSERT INTO groups
                   VALUES (%s, %s);''',
                   (netID, name))

def create_auditionees(cur):
    cur.execute('''CREATE TABLE IF NOT EXISTS auditionees
                   (netID varchar(50) PRIMARY KEY,
                    name varchar(50) NOT NULL,
                    classYear integer NOT NULL,
                    voicePart varchar(50),
                    dormRoom varchar(50) NOT NULL,
                    phoneNumber varchar(50));''')

def create_audition_times(cur):
    cur.execute('''CREATE TABLE IF NOT EXISTS auditionTimes
                   (auditionID SERIAL PRIMARY KEY,
                    auditioneeNetID varchar(50) NOT NULL,
                    groupNetID varchar(50) NOT NULL,
                    timeSlot timestamp NOT NULL)''')

def main():
    # Setup connection and cursor
    with connect(host=HOST, database=DATABASE, 
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            # Create the tables
            create_users(cur)
            create_groups(cur)
            create_auditionees(cur)
            create_audition_times(cur)

            # Add acaprez groups to database
            add_group(cur, 'nassoons', 'The Nassoons')
            add_group(cur, 'footnotes', 'The Footnotes')
            add_group(cur, 'tigerlillies', 'The Tigerlillies')
            add_group(cur, 'tigressions', 'The Tigressions')
            add_group(cur, 'wildcats', 'The Wildcats')
            add_group(cur, 'roaring20', 'Roaring 20')
            add_group(cur, 'katzenjammers', 'The Katzenjammers')
            add_group(cur, 'tigertones', 'The Tigertones')

            # Commit changes
            con.commit()


if __name__ == '__main__':
    main()