'''
This module enables testing of the database module, since if database is
the main module, there is a circular import between database.py and 
audition.py
'''
import database as db

if __name__ == "__main__":
    db.offer_callback("nassoons", "tdmanley")
    db.add_availability("tdmanley", "2022-09-01 12:00:00")