'''
Created this file based on the tutorial provided at:
https://www.digitalocean.com/community/tutorials/how-to-use-a-postgresql-database-in-a-flask-application
'''

from psycopg2 import connect

# Database specific variables:
HOST = 'ec2-3-230-238-86.compute-1.amazonaws.com'
DATABASE = 'd8tdd1oslp407c'
USER = 'cmjmzphzaovzef'
PSWD='79e77741d5870f7fd84ac66ddc04c0074e407ba91b548ebd847ee076d8092600'

#-----------------------------------------------------------------------
def create_users(cur):
    cur.execute('DROP TABLE IF EXISTS users;')
    cur.execute('''CREATE TABLE users
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
                    name varchar(50) NOT NULL, 
                    url varchar(50) NOT NULL);''')

def add_group(cur, netID, name, url):
    add_user(cur, netID, 'leader')
    cur.execute('''INSERT INTO groups
                   VALUES (%s, %s, %s);''',
                   (netID, name, url))

def create_auditionees(cur):
    cur.execute('DROP TABLE IF EXISTS auditionees;')
    cur.execute('''CREATE TABLE auditionees
                   (netID varchar(50) PRIMARY KEY,
                    firstName varchar(50) NOT NULL,
                    lastName varchar(50) NOT NULL,
                    classYear integer NOT NULL,
                    voicePart varchar(50),
                    dormRoom varchar(50) NOT NULL,
                    phoneNumber varchar(50));''')
#-----------------------------------------------------------------------
def create_audition_times(cur):
    cur.execute('DROP TABLE IF EXISTS auditionTimes;')
    cur.execute('''CREATE TABLE auditionTimes
                   (auditionID SERIAL PRIMARY KEY,
                    auditioneeNetID varchar(50),
                    groupNetID varchar(50) NOT NULL,
                    timeSlot timestamp NOT NULL,
                    callbackOffered boolean);''')
#-----------------------------------------------------------------------
def create_audition_days(cur):
    cur.execute('DROP TABLE IF EXISTS auditionDays;')
    cur.execute('''CREATE TABLE auditionDays 
                   (day timestamp PRIMARY KEY);''')

def create_accessibility(cur):
    cur.execute('DROP TABLE IF EXISTS accessibility;')
    cur.execute('''CREATE TABLE accessibility 
                   (isAccessible boolean PRIMARY KEY);''')
    # Default to being open
    cur.execute('''
                INSERT INTO accessibility (isAccessible)
                VALUES (TRUE);
                ''')
#-----------------------------------------------------------------------
def create_callback_sessions(cur):
    cur.execute('DROP TABLE IF EXISTS callbackSessions')
    cur.execute('''CREATE TABLE callbackDays
                   (sessionStart timestamp PRIMARY KEY);''')

def create_callback_offers(cur):
    cur.execute('DROP TABLE IF EXISTS callbackOffers;')
    cur.execute('''CREATE TABLE callbackOffers
                   (auditioneeNetID varchar(50) NOT NULL,
                    groupNetID varchar(50) NOT NULL,
                    accepted boolean NOT NULL);''')

def create_callback_availability(cur):
    cur.execute('DROP TABLE IF EXISTS callbackAvailability;')
    cur.execute('''CREATE TABLE callbackAvailability
                   (auditioneeNetID varchar(50) NOT NULL,
                    timeslot timestamp NOT NULL);''')

def create_callbacks(cur):
    cur.execute('DROP TABLE IF EXISTS callbacks;')
    cur.execute('''CREATE TABLE callbacks
                   (auditioneeNetID varchar(50) NOT NULL,
                    groupNetID varchar(50) NOT NULL,
                    timeslot timestamp NOT NULL);''')
#-----------------------------------------------------------------------
def reset_database():
    # Setup connection and cursor
    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            # Create the user tables
            create_users(cur)
            create_groups(cur)
            create_auditionees(cur)

            # Create the first round table
            create_audition_times(cur)

            # Create administrative tables
            create_audition_days(cur)
            create_accessibility(cur)

            # Create the callback tables
            create_callback_sessions(cur)
            create_callback_offers(cur)
            create_callback_availability(cur)
            create_callbacks(cur)

            # Add acaprez groups to database
            add_group(cur, 'nassoons', 'The Nassoons', 
            'http://www.nassoons.com/')
            add_group(cur, 'footnotes', 'The Footnotes', 
            'http://princetonfootnotes.com/')
            add_group(cur, 'tigerlillies', 'The Tigerlillies', 
            'https://www.putigerlilies.com/')
            add_group(cur, 'tigressions', 'The Tigressions', 
            'http://www.theprincetontigressions.com/')
            add_group(cur, 'wildcats', 'The Wildcats', 
            'https://www.princetonwildcats.com/')
            add_group(cur, 'roaring20', 'Roaring 20', 
            'https://www.princetonroaring20.com/')
            add_group(cur, 'katzenjammers', 'The Katzenjammers', 
            'http://www.theprincetonkatzenjammers.com/')
            add_group(cur, 'tigertones', 'The Tigertones', 
            'http://www.tigertones.com/')

            # Add generic admin user (should be a specific person)
            add_user(cur, 'admin', 'admin')

            # Commit changes
            con.commit()


if __name__ == '__main__':
    reset_database()
