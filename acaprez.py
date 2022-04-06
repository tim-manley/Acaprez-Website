#!/usr/bin/env python

#-----------------------------------------------------------------------
# acaprez.py
# Authors: Tim Manley
#-----------------------------------------------------------------------

from doctest import DocTestRunner
from os import remove, environ
from os import remove
import sched
from time import time
from unicodedata import name
from urllib import response
from xml.dom import domreg
from flask import Flask, request, make_response, redirect, url_for
from flask import render_template, session
from html import escape  # Used to thwart XSS attacks.
from cgi import FieldStorage
import database as db
from sys import stderr
from urllib.parse import unquote

#-----------------------------------------------------------------------

app = Flask(__name__)

import auth

# This should be made to work, but for alpha we can just hard code stuff
try:
    debug = environ['DEBUG']
    app.secret_key = environ['SECRET_KEY']
except KeyError:
    debug = True
    debug_netid = ''
    debug_perms = ''
    app.secret_key = b'\xbc>\xe0\xf8\xdf\x84\xe9aS\x02`i\x8e\xa1\xee\x92'
# debug = False
# app.secret_key = b'\xbc>\xe0\xf8\xdf\x84\xe9aS\x02`i\x8e\xa1\xee\x92'

#-----------------------------------------------------------------------

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    html = render_template('index.html')
    response = make_response(html)
    #clears any existing cookies, need to add back later
    #response.set_cookie('netID', '', max_age=0)
    return response

#-----------------------------------------------------------------------

@app.route('/login', methods=['GET'])
def login():
    if debug:
        session['username'] = debug_netid
        session['permissions'] = debug_perms

    html = render_template('caslogin.html')
    response = make_response(html)
    return response



#-----------------------------------------------------------------------

@app.route('/leader', methods=['GET'])
def leader():
    netID = auth.authenticate()
    if session.get('permissions') != 'leader':
        html = render_template('insufficient.html')
        response = make_response(html)
        return response
    auds = db.get_group_auditions(netID)
    times = db.get_group_times(netID)
    html = render_template('leader.html', netID=netID, auds=auds, times=times)
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/auditionee', methods=['GET'])
def auditionee():
    netID = auth.authenticate()
    print('username: ', session.get('username'))
    if session.get('permissions') == 'leader' or \
            session.get('username') is None or \
            session.get('username').strip() == '':
        html = render_template('insufficient.html')
        response = make_response(html)
        return response
    auditions = db.get_auditionee_auditions(netID)
    groups = db.get_groups()
    profile = db.get_auditionee(netID)
    if profile is None:
        welcome = 'Welcome, ' + str(netID) + '! Please create your profile.'
        html = render_template('editprofile.html', 
                                netID=netID, instruction=welcome,
                                year='', room='', voice='', phone=''
        )
    else:
        html = render_template('auditionee.html', auditions=auditions, profile=profile, groups=groups)
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/editprofile', methods=['GET'])
def editprofile():
    netID = auth.authenticate()
    if session.get('permissions') != 'auditionee':
        html = render_template('insufficient.html')
        response = make_response(html)
        return response
    user_instr = 'Fill out the form to change your profile.'
    user = db.get_auditionee(netID)
    html = render_template('editprofile.html', netID=netID, name=user.get_name(),
                            instruction=user_instr, year=user.get_class_year(),
                            dorm=user.get_dorm_room(), voice=user.get_voice_part(),
                            phone=user.get_phone_number())
    response = make_response(html)
    return response


#-----------------------------------------------------------------------

@app.route('/addtimes', methods=['GET'])
def addtimes():
    netID = auth.authenticate()
    if session.get('permissions') != 'leader':
        html = render_template('insufficient.html')
        response = make_response(html)
        return response

    scheduled_slots = db.get_group_times(netID)
    scheduled = []
    for slot in scheduled_slots:
        time = slot.get_timeslot().strftime('%Y-%m-%d %H:%M:%S')
        scheduled.append(time)

    html = render_template('addtimes.html',
                            netID=netID,
                            scheduled=scheduled)
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/addedtimes', methods=['GET', 'POST'])
def addedtimes():
    netID = auth.authenticate()
    if session.get('permissions') != 'leader':
        html = render_template('insufficient.html')
        response = make_response(html)
        return response

    times = request.form.getlist('times')
    for time in times:
        db.add_audition_time(netID, time)
    html = render_template('addedtimes.html')
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/confirmprofile', methods=['GET', 'POST'])
def confirmprofile():
    netID = auth.authenticate()
    if session.get('permissions') != 'auditionee' or \
            request.referrer.split()[-1] != 'editprofile':
        html = render_template('insufficient.html')
        response = make_response(html)
        return response

    name = request.form['name']
    year = int(request.form['year'])
    dorm = request.form['dorm']
    voice = request.form['voice']
    phone = request.form['phone']
    if db.get_auditionee(netID) is not None:
        db.update_auditionee(netID, name, year, dorm, voice, phone)
    else:
        db.add_auditionee(netID, name, year, dorm, voice, phone)

    html = render_template('confirmprofile.html', netID=netID, name=name,
                         year=year, dorm=dorm, voice=voice, phone=phone)
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/netID', methods=['GET'])
def netID():
    _ = auth.authenticate()
    if session.get('permissions') == 'leader':
        return redirect(url_for('leader'))
    else:
        return redirect(url_for('auditionee'))

#-----------------------------------------------------------------------

@app.route('/showgroupauditions', methods=['GET'])
def show_group_auditions():
    if request.referrer is None or request.referrer.split('/')[-1] != 'createAudition':
        html = render_template('insufficient.html')
        response = make_response(html)
        return response

    _ = auth.authenticate()
    if session.get('permissions') is None:
        html = render_template('insufficient.html')
        response = make_response(html)
        return response

    print('From: ' + str(request.referrer))
    groupNetID = request.args.get('groupNetID')
    available_auditions = db.get_group_availability(groupNetID)
    available = []
    for audition in available_auditions:
        time = audition.get_timeslot().strftime('%Y-%m-%d %H:%M:%S')
        available.append(time)
    html = render_template('auditioneeCalendar.html', available=available)
    response = make_response(html)
    return response


#-----------------------------------------------------------------------

@app.route('/createAudition', methods=['GET'])
def createAudition():
    _ = auth.authenticate()
    if session.get('permissions') != 'auditionee':
        html = render_template('insufficient.html')
        response = make_response(html)
        return response
    groups = db.get_groups()
    html = render_template('createAudition.html',
                            groups=groups)
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/auditioneeInfo', methods=['GET'])
def auditioneeInfo():
    netid = auth.authenticate()
    if session.get('permissions') != 'leader':
        html = render_template('insufficient.html')
        response = make_response(html)
        return response

    auditionee = db.get_auditionee(netid)
    html = render_template('auditioneeInfo.html', auditionee=auditionee)
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/signup-confirmation', methods=['GET', 'POST'])
def signup_confirmation():
    if request.referrer is None or request.referrer.split('/')[-1] != 'createAudition':
        html = render_template('insufficient.html')
        response = make_response(html)
        return response

    auditionee_netID = auth.authenticate()
    if session.get('permissions') != 'auditionee':
        html = render_template('insufficient.html')
        response = make_response(html)
        return response

    group_netID = request.args.get('group')
    time_slot = request.args.get('timeslot')
    group_netID = unquote(group_netID)
    time_slot = unquote(time_slot)
    db.audition_signup(auditionee_netID, group_netID, time_slot)
    html = render_template('signup-confirmation.html')
    response = make_response(html)
    return response

#Below here is for reference only
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
