#!/usr/bin/env python

#-----------------------------------------------------------------------
# acaprez.py
# Authors: Tim Manley
#-----------------------------------------------------------------------

from doctest import DocTestRunner
from math import perm
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
from init_db import reset_database
from sys import audit, stderr
from urllib.parse import unquote
import group

#-----------------------------------------------------------------------

app = Flask(__name__)

app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

import auth

# This should be made to work, but for alpha we can just hard code stuff
# try:
#     debug = environ['DEBUG']
#     app.secret_key = environ['SECRET_KEY']
# except KeyError:
#     debug = False
#     debug_netid = ''
#     app.secret_key = b'\xbc>\xe0\xf8\xdf\x84\xe9aS\x02`i\x8e\xa1\xee\x92'
# ----------------------------------------------------------------------
# env = environ.Env(
#     DEBUG=(bool, False),
#     SECRET_KEY=(str, b'\xbc>\xe0\xf8\xdf\x84\xe9aS\x02`i\x8e\xa1\xee\x92'),
#     DEBUG_NETID=(str, '')
# )
#
# READ_DOT_ENV_FILE = env.bool('READ_DOT_ENV_FILE', default=False)
# if READ_DOT_ENV_FILE:
#     environ.Env.read_env()

DEBUG = False
DEBUG_NETID = ''
app.secret_key = b'\xbc>\xe0\xf8\xdf\x84\xe9aS\x02`i\x8e\xa1\xee\x92'

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
    pending = db.get_group_pending_auditions(netID)
    offered = db.get_group_offered_callbacks(netID)
    for audition in offered:
        auditionee = db.get_auditionee(audition[0])
        audition.append(str(auditionee.get_firstname())+' '+str(auditionee.get_lastname()))
    times = db.get_group_times(netID)
    group = db.get_group(netID)
    group_name = group.get_name()
    html = render_template('leader.html', group_name=group_name, pending=pending, 
                            offered=offered, times=times, db=db)
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/admin', methods=['GET'])
def admin():
    _ = auth.authenticate()
    if session.get('permissions') != 'admin':
        html = render_template('insufficient.html')
        response = make_response(html)
        return response
    groups = db.get_groups()
    html = render_template('admin.html', groups=groups)
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/reset', methods=['POST'])
def reset():
    _ = auth.authenticate()
    if session.get('permissions') != 'admin':
        html = render_template('insufficient.html')
        response = make_response(html)
        return response

    dates = request.form['dates'].split(', ') # Parse dates input
    dates.sort() # Sort for formatting
    callback_dates = request.form.getlist('callbackdates[]') # Parse dates input
    callback_dates = list(set(callback_dates))
    callback_dates.sort()

    reset_database()
    if dates[0] != "": # Check whether any dates have been input
        for date in dates:
            db.add_audition_day(date)

    for date in callback_dates:
        if date != '':
            db.add_callback_session(date)
    return redirect(url_for('admin'))

#-----------------------------------------------------------------------

@app.route('/auditionee', methods=['GET'])
def auditionee():
    netID = auth.authenticate()
    if session.get('permissions') == 'leader' or \
        session.get('permissions') == 'admin' or \
            session.get('username') is None or \
            session.get('username').strip() == '':
        html = render_template('insufficient.html')
        response = make_response(html)
        return response
    auditions = db.get_auditionee_auditions(netID)
    for audition in auditions:
        audition.set_group()
   
    profile = db.get_auditionee(netID)
    if profile is None:
        welcome = 'Welcome, ' + str(netID) + '! Please create your profile.'
        html = render_template('editprofile.html', 
                                netID=netID, instruction=welcome,
                                year='', room='', voice='', phone=''
        )
    else:
        callbacks = db.get_pending_callbacks(netID) 
        accepted = db.get_accepted_callbacks(netID)
        num_accepted = len(accepted)
        num_offered = num_accepted + len(callbacks)
        if len(db.get_callback_availability(netID)) != 0:
            num_offered = 0 # So auditionee cannot sign up for more callback times

        html = render_template('auditionee.html', auditions=auditions, profile=profile,
                                    callbacks=callbacks, accepted=accepted, num_accepted=num_accepted,
                                    num_offered=num_offered)
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/cancelaudition', methods=['POST'])
def cancel_audition():
    _ = auth.authenticate()
    if session.get('permissions') != 'auditionee':
        html = render_template('insufficient.html')
        response = make_response(html)
        return response
    audition_id = request.args.get('auditionid')
    db.cancel_audition(audition_id) # Error handling ommitted
    return redirect(url_for('auditionee'))

#-----------------------------------------------------------------------

@app.route('/acceptcallback', methods=['POST'])
def accept_callback():
    netID = auth.authenticate()
    if session.get('permissions') != 'auditionee':
        html = render_template('insufficient.html')
        response = make_response(html)
        return response
    groupID = request.args.get('groupID')
    db.accept_callback(groupID, netID) # Error handling ommitted
    return redirect(url_for('auditionee'))

#-----------------------------------------------------------------------

@app.route('/offercallback', methods=['POST'])
def offer_callback():
    groupID = auth.authenticate()
    if session.get('permissions') != 'leader':
        html = render_template('insufficient.html')
        response = make_response(html)
        return response
    netID = request.args.get('netID')
    db.offer_callback(groupID, netID) # Error handling ommitted
    return redirect(url_for('leader'))

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
    html = render_template('editprofile.html', netID=netID, firstname=user.get_firstname(), 
                            lastname=user.get_lastname(),
                            instruction=user_instr, year=user.get_class_year(),
                            dorm=user.get_dorm_room(), voice=user.get_voice_part(),
                            phone=user.get_phone_number())
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/callbackavailability', methods=['GET'])
def callbackavailability():
    netID = auth.authenticate()
    if session.get('permissions') != 'auditionee':
        html = render_template('insufficient.html')
        response = make_response(html)
        return response

    # Setup the calendar
    dates = db.get_callback_sessions()
    fdays =[]
    days = []
    for date in dates:
        fday = date.strftime("%b %-d, %-I:%M %p")
        day = date.strftime("%Y-%m-%d %H:%M:%S")
        fdays.append(fday)
        days.append(day)

    scheduled_slots = db.get_callback_availability(netID)
    scheduled = []
    for slot in scheduled_slots:
        time = slot.strftime('%Y-%m-%d %H:%M:%S')
        scheduled.append(time)

    html = render_template('callbackavailability.html',
                            netID=netID,
                            fdays=fdays,
                            days=days,
                            scheduled=scheduled)
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/addedcallbacks', methods=['GET', 'POST'])
def addedcallbacks():
    netID = auth.authenticate()
    if session.get('permissions') != 'auditionee':
        html = render_template('insufficient.html')
        response = make_response(html)
        return response

    times = request.form.getlist('times')
    for time in times:
        db.add_callback_availability(netID, time)
    html = render_template('addedcallbacks.html')
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

    # Setup the calendar
    dates = db.get_audition_dates()
    fdays =[]
    days = []
    for date in dates:
        fday = date.strftime("%b %d")
        day = date.strftime("%Y-%m-%d")
        fdays.append(fday)
        days.append(day)

    scheduled_slots = db.get_group_times(netID)
    scheduled = []
    for slot in scheduled_slots:
        time = slot.get_timeslot().strftime('%Y-%m-%d %H:%M:%S')
        scheduled.append(time)

    html = render_template('addtimes.html',
                            netID=netID,
                            fdays=fdays,
                            days=days,
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
    '''html = render_template('addedtimes.html')
    response = make_response(html)'''
    return redirect(url_for('leader') + '#added')

#-----------------------------------------------------------------------

@app.route('/canceltime', methods=['POST'])
def canceltime():
    _ = auth.authenticate()
    if session.get('permissions') != 'leader':
        html = render_template('insufficient.html')
        response = make_response(html)
        return response

    auditionID = request.args.get('auditionID')
    db.remove_audition_time(auditionID)
    return redirect(url_for('leader'))

#-----------------------------------------------------------------------

@app.route('/confirmprofile', methods=['GET', 'POST'])
def confirmprofile():
    netID = auth.authenticate()
    if session.get('permissions') == 'leader' or \
        session.get('permissions') == 'admin' or \
        request.referrer is None or not \
        (request.referrer.split('/')[-1] == 'editprofile' or \
        request.referrer.split('/')[-1] == 'auditionee'):

        html = render_template('insufficient.html')
        response = make_response(html)
        return response
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    year = int(request.form['year'])
    dorm = request.form['dorm']
    voice = request.form['voice']
    phone = request.form['phone']
    if db.get_auditionee(netID) is not None:
        db.update_auditionee(netID, firstname, lastname, year, dorm, voice, phone)
    else:
        db.add_auditionee(netID, firstname, lastname, year, dorm, voice, phone)

    html = render_template('confirmprofile.html', netID=netID, firstname=firstname,
                        lastname=lastname, year=year, dorm=dorm, voice=voice, phone=phone)
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/netID', methods=['GET'])
def netID():
    _ = auth.authenticate()
    permission = session.get('permissions')
    if permission == 'leader':
        return redirect(url_for('leader'))
    elif permission == 'admin':
        return redirect(url_for('admin'))
    else:
        return redirect(url_for('auditionee'))

#-----------------------------------------------------------------------

# MUST DELETE BEFORE PUBLISHING
@app.route('/bypasslogin', methods=['GET'])
def bypass():
    netID = request.args.get('netID')
    permission = db.get_permissions(netID)
    session['username'] = netID
    session['permissions'] = permission
    if permission == 'leader':
        return redirect(url_for('leader'))
    elif permission == 'admin':
        return redirect(url_for('admin'))
    else:
        return redirect(url_for('auditionee'))

#-----------------------------------------------------------------------

@app.route('/showgroupauditions', methods=['GET'])
def show_group_auditions():
    if request.referrer is None or request.referrer.split('/')[-1] != 'createAudition':
        html = render_template('insufficient.html')
        response = make_response(html)
        return response

    netID = auth.authenticate()
    if session.get('permissions') != 'auditionee':
        html = render_template('insufficient.html')
        response = make_response(html)
        return response

    # Setup the calendar
    dates = db.get_audition_dates()
    fdays =[]
    days = []
    for date in dates:
        fday = date.strftime("%b %d")
        day = date.strftime("%Y-%m-%d")
        fdays.append(fday)
        days.append(day)
    groupNetID = request.args.get('groupNetID')
    available_auditions = db.get_group_availability(groupNetID, netID)
    available = []
    for audition in available_auditions:
        time = audition.get_timeslot().strftime('%Y-%m-%d %H:%M:%S')
        available.append(time)
    html = render_template('auditioneeCalendar.html',
                            fdays=fdays,
                            days=days,
                            available=available)
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/showgroupcallbacks', methods=['GET'])
def show_group_callbacks():
    if request.referrer is None or request.referrer.split('/')[-1] != 'admin':
        html = render_template('insufficient.html')
        response = make_response(html)
        return response

    _ = auth.authenticate()
    if session.get('permissions') != 'admin':
        html = render_template('insufficient.html')
        response = make_response(html)
        return response

    # Setup the calendar
    groupNetID = request.args.get('groupNetID')
    entries = []
    sessiondt = db.get_callback_sessions()
    for netID in db.get_group_accepted_callbacks(groupNetID):
        auditionee = db.get_auditionee(netID)
        name = auditionee.get_firstname() + " " + auditionee.get_lastname()
        year = auditionee.get_class_year()
        voice = auditionee.get_voice_part()
        alt_group = ''
        for group in db.get_accepted_callbacks(netID):
            if group.get_netID() != groupNetID:
                alt_group = group.get_name()

        entry = [name, year, voice, alt_group]
        availability = db.get_callback_availability(netID)
        for time in sessiondt:
            if time in availability:
                entry.append('Available')
            else:
                entry.append('')
        entries.append(entry) 
    
    dates = []
    times = []
    for sesh in sessiondt:

        dates.append(sesh.strftime("%b %-d"))
        times.append(sesh.strftime("%-I:%M %p"))

    html = render_template('availabilityCalendar.html',
                            dates=dates, times=times,
                            entries=entries, group=groupNetID)
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
    _ = auth.authenticate()
    if session.get('permissions') != 'leader':
        html = render_template('insufficient.html')
        response = make_response(html)
        return response

    netid = request.args.get('netID')
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

    auditions = db.get_auditionee_auditions(auditionee_netID)
    group_netID = request.args.get('group')
    for audition in auditions:
        if group_netID == audition.get_group():
            audition.set_group()
            grp_name = audition.get_group_name()
            html = f'''
                    <div class="alert alert-warning fade show" role="alert">
                        Already signed up for audition with {grp_name}
                    </div>
                   '''
            response = make_response(html)
            return response

    time_slot = request.args.get('timeslot')
    group_netID = unquote(group_netID)
    time_slot = unquote(time_slot)
    db.audition_signup(auditionee_netID, group_netID, time_slot)
    html = f'''
                <div class="alert alert-success fade show" role="alert">
                    Successfully signed up for audition at {time_slot}
                </div>
            '''
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/about', methods=['GET'])
def about():
    _ = auth.authenticate()
    groups = db.get_groups()
    html = render_template('about.html',
                            groups=groups)
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

@app.route('/logoutconfirmation', methods=['GET'])
def logoutconfirmation():
    _ = auth.authenticate()
    prev_url = request.referrer
    if prev_url is not None:
        prev_url = prev_url.split('/')[-1]
    else:
        prev_url = "index"
    html = render_template('confirmLogout.html',
                           url=prev_url)
    response = make_response(html)
    return response
