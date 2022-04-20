'''
This module enables testing of the database module, since if database is
the main module, there is a circular import between database.py and 
audition.py
'''
import database as db

if __name__ == "__main__":
    db.accept_callback("footnotes", "tdmanley")
    for group in db.get_accepted_callbacks("tdmanley"):
        print(group.get_name())