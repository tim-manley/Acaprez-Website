'''
This module enables testing of the database module, since if database is
the main module, there is a circular import between database.py and 
audition.py
'''
from datetime import datetime
from multiprocessing.dummy import Value
from unittest import TestCase as tc
import unittest

import psycopg2
import database as db
from audition import Audition
from auditionee import Auditionee
from group import Group
from init_db import reset_database
from psycopg2 import connect
from datetime import datetime

# Database specific variables:
HOST = 'ec2-3-230-238-86.compute-1.amazonaws.com'
DATABASE = 'd8tdd1oslp407c'
USER = 'cmjmzphzaovzef'
PSWD='79e77741d5870f7fd84ac66ddc04c0074e407ba91b548ebd847ee076d8092600'

def test_add_audition_day():
    # Call the function
    db.add_audition_day("2022-09-01 00:00:00")

    # Check it is correct using direct call to database
    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''SELECT * FROM auditionDays;''')
            rows = cur.fetchall()
            assert len(rows) == 1, 'incorrect number of rows'
            row = rows[0]
            assert row[0] == datetime(2022, 9, 1)

def test_add_audition_time():
    # Call the function
    db.add_audition_time('nassoons', '2022-09-01 17:00:00')

    # Check it is correct using direct call to database
    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''SELECT * FROM auditionTimes;''')
            rows = cur.fetchall()
            assert len(rows) == 1, 'incorrect number of rows'
            row = rows[0]
            assert isinstance(row[0], int)
            assert row[1] is None
            assert row[2] == 'nassoons'
            assert row[3] == datetime(2022, 9, 1, 17, 0, 0)
            assert row[4] == False

def test_remove_audition_time():
    # Call the function
    db.remove_audition_time(1)

    # Check it is correct using direct call to database
    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''SELECT * FROM auditionTimes;''')
            rows = cur.fetchall()
            assert len(rows) == 0, 'incorrect number of rows'

def test_add_auditionee():
    # Call the function
    db.add_auditionee("testID", "Test", "Person", 2024, "A100", "Bass",
    "123-456-7890")

    # Check it is correct using direct call to database
    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''SELECT * FROM auditionees;''')
            rows = cur.fetchall()
            assert len(rows) == 1, 'incorrect number of rows'
            row = rows[0]
            assert row[0] == "testID"
            assert row[1] == "Test"
            assert row[2] == "Person"
            assert row[3] == 2024
            assert row[4] == "Bass"
            assert row[5] == "A100"
            assert row[6] == "123-456-7890"
            cur.execute('''SELECT * FROM users;''')
            rows = cur.fetchall()
            assert len(rows) == 10, 'incorrect number of rows'
            cur.execute('''SELECT * FROM users WHERE netID=%s''',
            ('testID',))
            rows = cur.fetchall()
            assert len(rows) == 1, 'wrong number of users with netID'
            row = rows[0]
            assert row[0] == "testID"
            assert row[1] == "auditionee"
 
def test_update_auditionee():
    # Call the function
    db.update_auditionee("testID", "Tester", "Persona", 2025, "A101", "Tenor",
    "123-456-7891")

    # Check it is correct using direct call to database
    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''SELECT * FROM auditionees;''')
            rows = cur.fetchall()
            assert len(rows) == 1, 'incorrect number of rows'
            row = rows[0]
            assert row[0] == "testID"
            assert row[1] == "Tester"
            assert row[2] == "Persona"
            assert row[3] == 2025
            assert row[4] == "Tenor"
            assert row[5] == "A101"
            assert row[6] == "123-456-7891"
            cur.execute('''SELECT * FROM users;''')
            rows = cur.fetchall()
            assert len(rows) == 10, 'incorrect number of rows'
            cur.execute('''SELECT * FROM users WHERE netID=%s''',
            ('testID',))
            rows = cur.fetchall()
            assert len(rows) == 1, 'wrong number of users with netID'
            row = rows[0]
            assert row[0] == "testID"
            assert row[1] == "auditionee"

def test_audition_signup():
    # Create an audition time (already tested at this point)
    db.add_audition_time('nassoons', '2022-09-01 17:00:00')
    # Call the function
    db.audition_signup('testID', 'nassoons', '2022-09-01 17:00:00')

    # Check it is correct using direct call to database
    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''SELECT * FROM auditionTimes 
                           WHERE auditioneeNetID=%s;''', ('testID',))
            rows = cur.fetchall()
            assert len(rows) == 1, 'incorrect number of rows'
            row = rows[0]
            assert isinstance(row[0], int)
            assert row[1] == 'testID'
            assert row[2] == 'nassoons'
            assert row[3] == datetime(2022, 9, 1, 17, 0, 0)
            assert row[4] == False
    
    # Parameter validation testing

    # Add another time
    db.add_audition_time('nassoons', '2022-09-01 17:30:00')
    tc = unittest.TestCase()
    with tc.assertRaises(ValueError):
        db.audition_signup(20, 'nassoons', '2022-09-01 17:30:00')
    with tc.assertRaises(ValueError):
        db.audition_signup('testID', 20, '2022-09-01 17:30:00')
    with tc.assertRaises(ValueError):
        db.audition_signup('testID', 'nassoons', 20)
    with tc.assertRaises(BaseException):
        db.audition_signup('testID', 'nasoons', 'invalid')
    with tc.assertRaises(ValueError):
        db.audition_signup('testID', 'nonExistent', '2022-09-01 17:30:00')
    with tc.assertRaises(ValueError):
        # Non existent time
        db.audition_signup('testID', 'nassoons', '2022-09-01 21:00:00')
    with tc.assertRaises(ValueError):
        # Signing up for an already signed up for audition
        db.audition_signup('testID', 'nassoons', '2022-09-01 17:00:00')
    
    # Remove time (for other tests' sake)
    db.remove_audition_time(3)
    


def test_cancel_audition():
    # Call the function
    db.cancel_audition('2')

    # Check it is correct using direct call to database
    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''SELECT * FROM auditionTimes;''')
            rows = cur.fetchall()
            assert len(rows) == 1, 'incorrect number of rows'
            row = rows[0]
            assert isinstance(row[0], int)
            assert row[1] is None
            assert row[2] == 'nassoons'
            assert row[3] == datetime(2022, 9, 1, 17, 0, 0)
            assert row[4] == False

def test_offer_callback():
    # First resignup for audition
    db.audition_signup('testID', 'nassoons', '2022-09-01 17:00:00')
    # Call the function
    db.offer_callback('nassoons', 'testID')

    # Check it is correct using direct call to database
    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''SELECT * FROM auditionTimes;''')
            rows = cur.fetchall()
            assert len(rows) == 1, 'incorrect number of rows'
            row = rows[0]
            assert isinstance(row[0], int)
            assert row[1] == 'testID'
            assert row[2] == 'nassoons'
            assert row[3] == datetime(2022, 9, 1, 17, 0, 0)
            assert row[4] == True
            cur.execute('''SELECT * FROM callbackOffers;''')
            rows = cur.fetchall()
            assert len(rows) == 1, 'incorrect number of rows'
            row = rows[0]
            assert row[0] == 'testID'
            assert row[1] == 'nassoons'
            assert row[2] == False

def test_accept_callback():
    # Call the function
    db.accept_callback('nassoons', 'testID')

    # Check it is correct using direct call to database
    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''SELECT * FROM auditionTimes;''')
            rows = cur.fetchall()
            assert len(rows) == 1, 'incorrect number of rows'
            row = rows[0]
            assert isinstance(row[0], int)
            assert row[1] == 'testID'
            assert row[2] == 'nassoons'
            assert row[3] == datetime(2022, 9, 1, 17, 0, 0)
            assert row[4] == True
            cur.execute('''SELECT * FROM callbackOffers;''')
            rows = cur.fetchall()
            assert len(rows) == 1, 'incorrect number of rows'
            row = rows[0]
            assert row[0] == 'testID'
            assert row[1] == 'nassoons'
            assert row[2] == True

def test_add_callback_session():
    # Call the function
    db.add_callback_session('2022-09-02 12:00:00')

    # Check it is correct using direct call to database
    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''SELECT * FROM callbackSessions;''')
            rows = cur.fetchall()
            assert len(rows) == 1, 'incorrect number of rows'
            row = rows[0]
            assert row[0] == datetime(2022, 9, 2, 12, 0, 0)

def test_add_callback_availability():
    # Call the function
    db.add_callback_availability('testID', '2022-09-02 12:00:00')

    # Check it is correct using direct call to database
    with connect(host=HOST, database=DATABASE,
                 user=USER, password=PSWD) as con:
        with con.cursor() as cur:
            cur.execute('''SELECT * FROM callbackAvailability;''')
            rows = cur.fetchall()
            assert len(rows) == 1, 'incorrect number of rows'
            row = rows[0]
            assert row[0] == 'testID'
            assert row[1] == datetime(2022, 9, 2, 12, 0, 0)

def test_get_group():
    # Call the function
    group = db.get_group('nassoons')

    # Check correctness
    assert isinstance(group, Group)
    assert group.get_netID() == 'nassoons'
    assert group.get_name() == 'The Nassoons'
    assert group.get_url() == 'http://www.nassoons.com/'

def test_get_groups():
    # Call the function
    groups = db.get_groups()

    # Check correctness TODO: Add more rigour
    assert len(groups) == 8, 'wrong number of groups returned'
    for group in groups:
        assert isinstance(group, Group)

def test_get_auditionee():
    # Call the function
    auditionee = db.get_auditionee('testID')
    
    # Check correctness
    assert isinstance(auditionee, Auditionee)
    assert auditionee.get_netID() == 'testID'
    assert auditionee.get_firstname() == 'Tester'
    assert auditionee.get_lastname() == 'Persona'
    assert auditionee.get_class_year() == 2025
    assert auditionee.get_voice_part() == 'Tenor'
    assert auditionee.get_dorm_room() == 'A101'
    assert auditionee.get_phone_number() == '123-456-7891'

def test_get_group_availability():
    # Add some available auditions
    for i in range(12, 16):
        for j in range(0, 46, 15):
            db.add_audition_time('nassoons', f'2022-09-01 {i}:{j}:00')
    
    # Call the function
    available_auditions = db.get_group_availability('nassoons')

    assert len(available_auditions) == 16
    for audition in available_auditions:
        audition.set_group()
        assert isinstance(audition, Audition)
        assert audition.get_group() == 'nassoons'
        assert audition.get_auditionee_netID() is None

if __name__ == "__main__":
    print("Starting testing")
    
    # First reset the database entirely
    print("Resetting database")
    reset_database()
    print("Database reset")
    
    # Next test those functions which modify the database
    print("Testing: add_audition_day")
    test_add_audition_day()
    print("add_audition_day passed tests.")
    print("Testing: add_audition_time")
    test_add_audition_time()
    print("add_audition_time passed tests.")
    print("Testing: remove_audition_time")
    test_remove_audition_time()
    print("remove_audition_time passed tests.")
    print("Testing: add_auditionee")
    test_add_auditionee()
    print("add_auditionee passed tests.")
    print("Testing: update_auditionee")
    test_update_auditionee()
    print("update_auditionee passed tests.")
    print("Testing: audition_signup")
    test_audition_signup()
    print("audition_signup passed tests.")
    print("Testing: cancel_audition")
    test_cancel_audition()
    print("cancel_audition passed tests.")
    print("Testing: offer_callback")
    test_offer_callback()
    print("offer_callback passed tests.")
    print("Testing: accept_callback")
    test_accept_callback()
    print("accept_callback passed tests.")
    print("Testing: add_callback_session")
    test_add_callback_session()
    print("add_callback_session passed tests.")
    print("Testing: add_callback_availability")
    test_add_callback_availability()
    print("add_callback_availability passed tests.")
    
    # Finally test those functions which do not modify the database
    print("Testing: get_group")
    test_get_group()
    print("get_group passed tests.")
    print("Testing: get_groups")
    test_get_groups()
    print("get_groups passed tests.")
    print("Testing: get_auditionee")
    test_get_auditionee()
    print("get_auditionee passed tests.")
    print("Testing: get_group_availability")
    test_get_group_availability()
    print("get_group_availability passed tests.")
    '''
    TODO:
    test_get_group_auditions()
    test_get_group_pending_auditions()
    test_get_group_offered_callbacks()
    test_get_group_times()
    test_get_auditionee_auditions()
    test_get_permissions()
    test_get_audition_dates()
    test_is_available_audition()
    test_get_accepted_callbacks()
    test_get_pending_callbacks()
    test_get_group_accepted_callbacks()
    test_get_callback_sessions()
    test_get_callback_availability()
    '''
    print("All tests passed!")