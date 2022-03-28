#!/usr/bin/env python

#-----------------------------------------------------------------------
# acaprez.py
# Authors: Tim Manley
#-----------------------------------------------------------------------

from flask import Flask, request, make_response, redirect, url_for
from flask import render_template
from http.cookies import SimpleCookie
from html import escape  # Used to thwart XSS attacks.
from cgi import FieldStorage
import database as db
from sys import stderr

#-----------------------------------------------------------------------

app = Flask(__name__)

#-----------------------------------------------------------------------

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():

    html = render_template('index.html')
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/login', methods=['GET'])
def login():

    html = render_template('login.html')
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/leader', methods=['GET'])
def leader():

    html = render_template('leader.html')
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/auditioneelanding', methods=['GET', 'POST'])
def setcookie():
    netID = request.form['netID']
    auditions = db.get_auditionee_auditions(netID)
    html = render_template('auditionee.html', auditions=auditions, netID=netID)
    response = make_response(html)
    response.set_cookie('netID', netID)
    return response

#-----------------------------------------------------------------------

@app.route('/auditionee', methods=['GET'])
def auditionee():
    netID = request.cookies.get('netID')
    auditions = db.get_auditionee_auditions(netID)
    html = render_template('auditionee.html', auditions=auditions, netID=netID)
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/netID', methods=['GET'])
def netID():
    html = render_template('netID.html')
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/netIDleader', methods=['GET'])
def netIDleader():
    html = render_template('netIDleader.html')
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/leaderlanding', methods=['GET', 'POST'])
def leadercookie():
    netID = request.form['netID']
    html = render_template('leader.html', netID=netID)
    response = make_response(html)
    response.set_cookie('netID', netID)
    return response

#-----------------------------------------------------------------------

@app.route('/createAudition', methods=['GET'])
def createAudition():
    groups = db.get_groups()
    html = render_template('createAudition.html',
                            groups=groups)
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/signup-confirmation', methods=['GET', 'POST'])
def signup_confirmation():
    auditionee_netID = request.cookies.get('netID')
    group_netID = request.form['selected_group']
    time_slot = request.form['audition_timeslot']
    db.audition_signup(auditionee_netID, group_netID, time_slot)
    html = render_template('signup-confirmation.html')
    response = make_response(html)
    return response

#Below here is for reference only
'''@app.route('/searchform', methods=['GET'])
def search_form():

    error_msg = request.args.get('error_msg')
    if error_msg is None:
        error_msg = ''

    prev_author = request.cookies.get('prev_author')
    if prev_author is None:
        prev_author = '(None)'

    html = render_template('searchform.html',
        ampm=get_ampm(),
        current_time=get_current_time(),
        error_msg=error_msg,
        prev_author=prev_author)
    response = make_response(html)
    return response'''

#-----------------------------------------------------------------------

'''@app.route('/searchresults', methods=['GET'])
def search_results():

    author = request.args.get('author')
    if (author is None) or (author.strip() == ''):
        error_msg = 'Please type an author name.'
        return redirect(url_for('search_form', error_msg=error_msg))

    books = search(author)  # Exception handling omitted

    html = render_template('searchresults.html',
        ampm=get_ampm(),
        current_time=get_current_time(),
        author=author,
        books=books)
    response = make_response(html)
    response.set_cookie('prev_author', author)
    return response'''
