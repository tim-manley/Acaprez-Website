from pydoc import cli
import re
from sys import stderr
from urllib import response
import pytest
import urllib
from acaprez import app as aca
import database as db
#from flask import session

@pytest.fixture()
def app():
    app = aca
    app.config.update({
        "TESTING": True,
    })
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

def test_reset_database(client):
    with client.session_transaction() as session:
        session['username'] = 'admin'
        session['permissions'] = 'admin'
    response = client.post('/reset', data={
        'dates': '2022-09-01, 2022-09-02, 2022-09-03',
        'callbackdates[]': '2022-09-04'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_reset_insufficient(client):
    with client.session_transaction() as session:
        session['username'] = 'testID'
        session['permissions'] = 'auditionee'
    response = client.post('/reset', data={
        'dates': '2022-09-01, 2022-09-02, 2022-09-03'
    }, follow_redirects=True)
    assert b'<h4 id="insufficient-perms">Sorry, you do not have the necessary permissions to view this page.</h4>' in response.data

def test_index(client):
    response = client.get('/index')
    assert b'<a href="/netID" id="login" class="btn btn-primary" role="button">Log In</a>' in response.data
    assert b"<h2>Welcome!</h2>" in response.data

def test_dev_login(client):
    response = client.get('/login')
    assert b'<h2>Developer Login:</h2>' in response.data

def test_net_id(client):
    with client.session_transaction() as session:
        session['username'] = 'testID'
        session['permissions'] = 'auditionee'
    response = client.get('/netID')
    assert response.status_code == 302 # Check for redirect
    with client.session_transaction() as session:
        session['username'] = 'admin'
        session['permissions'] = 'admin'
    response = client.get('/netID')
    assert response.status_code == 302 # Check for redirect
    with client.session_transaction() as session:
        session['username'] = 'nassoons'
        session['permissions'] = 'leader'
    response = client.get('/netID')
    assert response.status_code == 302 # Check for redirect

def test_bypass(client):
    response = client.get('/bypasslogin?netID=nassoons')
    assert response.status_code == 302 # Check for redirect
    response = client.get('/bypasslogin?netID=testID')
    assert response.status_code == 302 # Check for redirect
    response = client.get('/bypasslogin?netID=admin')
    assert response.status_code == 302 # Check for redirect

def test_new_auditionee(client):
    with client.session_transaction() as session:
        session['username'] = 'testID'
        session['permissions'] = 'auditionee'
    response = client.get('/auditionee')
    assert b'<h1 id="welcome">Welcome, testID! Please create your profile.</h1>' in response.data

def test_confirm_profile(client):
    with client.session_transaction() as session:
        session['username'] = 'testID'
        session['permissions'] = 'auditionee'
    response = client.post('/confirmprofile', data={
        'firstname': 'Test',
        'lastname': 'Person',
        'year': '2024',
        'dorm': 'F100',
        'voice': 'Bass',
        'phone': '123-456-7890'
    }, headers={
        "Referer": '/auditionee'
    })
    assert b'<li class="list-group-item list-group-item-warning">First Name: Test </li>' in response.data
    assert b'<li class="list-group-item list-group-item-light">Phone Number: 123-456-7890 </li>' in response.data

def test_existing_auditionee(client):
    with client.session_transaction() as session:
        session['username'] = 'testID'
        session['permissions'] = 'auditionee'
    response = client.get('/auditionee')
    assert b'<h1 id="welcome">Welcome, Test Person!</h1>' in response.data

def test_edit_profile(client):
    with client.session_transaction() as session:
        session['username'] = 'testID'
        session['permissions'] = 'auditionee'
    response = client.get('/editprofile')
    assert b'<h1 id="welcome">Fill out the form to change your profile.</h1>' in response.data

def test_auditionee_insufficient(client):
    with client.session_transaction() as session:
        session['username'] = 'nassoons'
        session['permissions'] = 'leader'
    response = client.get('/auditionee')
    assert b'<h4 id="insufficient-perms">Sorry, you do not have the necessary permissions to view this page.</h4>' in response.data

def test_leader(client):
    with client.session_transaction() as session:
        session['username'] = 'nassoons'
        session['permissions'] = 'leader'
    response = client.get('/leader')
    assert b'<h1 id="welcome">Welcome, group leader of The Nassoons</h1>' in response.data

def test_add_times(client):
    with client.session_transaction() as session:
        session['username'] = 'nassoons'
        session['permissions'] = 'leader'
    response = client.get('/addtimes')
    assert b'<h2>Add Audition Times: </h2>' in response.data
    assert b'<th class="table_header">Sep 01</th>' in response.data
    assert b'<th class="table_header">Sep 02</th>' in response.data
    assert b'<th class="table_header">Sep 03</th>' in response.data

def test_added_times(client):
    with client.session_transaction() as session:
        session['username'] = 'nassoons'
        session['permissions'] = 'leader'
    response = client.post('/addedtimes', data={
        'times': ['2022-09-01 17:00:00',
                  '2022-09-01 17:15:00',
                  '2022-09-01 17:30:00']
    }, follow_redirects=True)
    assert b'<td>Sep 01 - 05:00 PM</td>' in response.data
    assert b'<td>Sep 01 - 05:15 PM</td>' in response.data
    assert b'<td>Sep 01 - 05:30 PM</td>' in response.data

def test_remove_time(client):
    with client.session_transaction() as session:
        session['username'] = 'nassoons'
        session['permissions'] = 'leader'
    response = client.post('/canceltime?auditionID=3')
    assert response.status_code == 302

def test_leader_insufficient(client):
    with client.session_transaction() as session:
        session['username'] = 'testID'
        session['permissions'] = 'auditionee'
    response = client.get('/leader')
    assert b'<h4 id="insufficient-perms">Sorry, you do not have the necessary permissions to view this page.</h4>' in response.data

def test_admin_insufficient(client):
    with client.session_transaction() as session:
        session['username'] = 'testID'
        session['permissions'] = 'auditionee'
    response = client.get('/admin')
    assert b'<h4 id="insufficient-perms">Sorry, you do not have the necessary permissions to view this page.</h4>' in response.data

def test_create_audition(client):
    with client.session_transaction() as session:
        session['username'] = 'testID'
        session['permissions'] = 'auditionee'
    response = client.get('/createAudition')
    assert b'<h2>Sign up for an audition: </h2>' in response.data

def test_view_group_auditions(client):
    with client.session_transaction() as session:
        session['username'] = 'testID'
        session['permissions'] = 'auditionee'
    response = client.get('/showgroupauditions?groupNetID=nassoons', headers={
        'Referer': '/createAudition'
    })
    assert b'''<button id="2022-09-01 17:00:00" type="button" class="btn btn-primary" style="width:100%">
                Available
            </button>''' in response.data

def test_audition_signup(client):
    with client.session_transaction() as session:
        session['username'] = 'testID'
        session['permissions'] = 'auditionee'
    response = client.post('/signup-confirmation?group=nassoons&timeslot=2022-09-01 17:00:00', headers={
        'Referer': '/createAudition'
    })
    assert b'''
                <div class="alert alert-success fade show" role="alert">
                    Successfully signed up for audition at 2022-09-01 17:00:00
                </div>
            ''' in response.data
    response = client.post('/signup-confirmation?group=nassoons&timeslot=2022-09-01 17:15:00', headers={
        'Referer': '/createAudition'
    })
    assert b'<div class="alert alert-warning fade show" role="alert">\n                        Already signed up for audition with The Nassoons\n                    </div>' in response.data

def test_pending_appears(client):
    with client.session_transaction() as session:
        session['username'] = 'nassoons'
        session['permissions'] = 'leader'
    response = client.get('/leader')
    assert b'<a\n                                href="auditioneeInfo?netID=testID">Test Person</a>' in response.data

def test_cancel_audition(client):
    with client.session_transaction() as session:
        session['username'] = 'testID'
        session['permissions'] = 'auditionee'
    id = urllib.parse.urlencode({"auditionid": 1})
    response = client.post('/cancelaudition?'+id, follow_redirects=True)
    assert b'<td>Sep 01 - 05:00 PM </td>' not in response.data # Check audition removed
    client.post('/signup-confirmation?group=nassoons&timeslot=2022-09-01 17:00:00', headers={
        'Referer': '/createAudition'
    }) # Resign up for audition

def test_offer_callback(client):
    with client.session_transaction() as session:
        session['username'] = 'testID'
        session['permissions'] = 'auditionee'
    response = client.post('/offercallback?netID=testID')
    assert b'<h4 id="insufficient-perms">Sorry, you do not have the necessary permissions to view this page.</h4>' in response.data
    with client.session_transaction() as session:
        session['username'] = 'nassoons'
        session['permissions'] = 'leader'
    response = client.post('/offercallback?netID=testID')
    assert response.status == '302 FOUND' # Check for redirect

def test_callback_appeared(client):
    with client.session_transaction() as session:
        session['username'] = 'testID'
        session['permissions'] = 'auditionee'
    response = client.get('/auditionee')
    assert b'<a href="http://www.nassoons.com/" target="_blank">The Nassoons</a>' in response.data

def test_accept_callback(client):
    with client.session_transaction() as session:
        session['username'] = 'testID'
        session['permissions'] = 'auditionee'
    response = client.post('/acceptcallback?groupID=nassoons')
    assert '302' in response.status

def test_callback_shows(client):
    with client.session_transaction() as session:
        session['username'] = 'nassoons'
        session['permissions'] = 'leader'
    response = client.get('/leader')
    assert b'<a href="auditioneeInfo?netID=testID"\n                                >Test Person</a>' in response.data

def test_callback_availability(client):
    with client.session_transaction() as session:
        session['username'] = 'testID'
        session['permissions'] = 'auditionee'
    response = client.get('/callbackavailability')
    assert b'<input type="checkbox" name="times" value="2022-09-04 00:00:00">' in response.data

def test_added_callbacks(client):
    with client.session_transaction() as session:
        session['username'] = 'testID'
        session['permissions'] = 'auditionee'
    response = client.post('/addedcallbacks', data={
        'times':'2022-09-04 00:00:00'
    })
    assert response.status_code == 200

def test_view_callback_availability(client):
    with client.session_transaction() as session:
        session['username'] = 'admin'
        session['permissions'] = 'admin'
    response = client.get('/showgroupcallbacks?groupNetID=nassoons', headers={
        'Referer':'/admin'
    })
    assert b'''<tr>
        
        <td style="text-align:center">Test Person</td>
        
        <td style="text-align:center">2024</td>
        
        <td style="text-align:center">Bass</td>
        
        <td style="text-align:center"></td>
        
        <td style="text-align:center">Available</td>
        
    </tr>''' in response.data

def test_about(client):
    with client.session_transaction() as session:
        session['username'] = 'testID'
        session['permissions'] = 'auditionee'
    response = client.get('/about')
    assert b'<h1>About Acaprez</h1>' in response.data

def test_auditionee_info(client):
    with client.session_transaction() as session:
        session['username'] = 'nassoons'
        session['permissions'] = 'leader'
    response = client.get('/auditioneeInfo?netID=testID')
    assert b'<li class="list-group-item list-group-item-warning">First Name: Test </li>' in response.data

def test_cas(client):
    response = client.get('/netID')
    assert response.status_code == 302

def test_logout(client):
    with client.session_transaction() as session:
        session['username'] = 'nassoons'
        session['permissions'] = 'leader'
    response = client.get('/logoutconfirmation')
    assert response.status_code == 200


def test_update_auditionee(client):
    with client.session_transaction() as session:
        session['username'] = 'testID'
        session['permissions'] = 'auditionee'
    response = client.post('/confirmprofile', data={
        'firstname': 'Test',
        'lastname': 'Person',
        'year': '2024',
        'dorm': 'F100',
        'voice': 'Bass',
        'phone': '123-456-7890'
    }, headers={
        "Referer": '/auditionee'
    })
    assert b'<li class="list-group-item list-group-item-warning">First Name: Test </li>' in response.data
    assert b'<li class="list-group-item list-group-item-light">Phone Number: 123-456-7890 </li>' in response.data