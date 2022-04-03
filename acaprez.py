#!/usr/bin/env python

#-----------------------------------------------------------------------
# acaprez.py
# Authors: Tim Manley
#-----------------------------------------------------------------------

from doctest import DocTestRunner
from os import remove
from unicodedata import name
from urllib import response
from xml.dom import domreg
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
    #clears any existing cookies, need to add back later
    #response.set_cookie('netID', '', max_age=0)
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
    groups = db.get_groups()
    profile = db.get_auditionee(netID)
    if profile is None:
        welcome = 'Welcome, ' + str(netID) + '! Please create your profile.'
        html = render_template('editprofile.html', 
                                netID=netID, instruction=welcome,
                                year='', room='', voice='', phone=''
        )
    else:
        html = render_template('auditionee.html',
                           auditions=auditions,
                           profile=profile,
                           groups=groups)
    response = make_response(html)
    response.set_cookie('netID', netID)
    return response

#-----------------------------------------------------------------------

@app.route('/auditionee', methods=['GET'])
def auditionee():
    netID = request.cookies.get('netID')
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
    netID = request.cookies.get('netID')
    user_instr = 'Fill out the form to change your profile.'
    user = db.get_auditionee(netID)
    html = render_template('editprofile.html', netID=netID, name=user.get_name(),
                            instruction=user_instr, year=user.get_class_year(),
                            dorm=user.get_dorm_room(), voice=user.get_voice_part(),
                            phone=user.get_phone_number())
    response = make_response(html)
    return response


#-----------------------------------------------------------------------

@app.route('/confirmprofile', methods=['GET', 'POST'])
def confirmprofile():
    name = request.form['name']
    year = int(request.form['year'])
    dorm = request.form['dorm']
    voice = request.form['voice']
    phone = request.form['phone']
    netID = request.cookies.get('netID')
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

@app.route('/showgroupauditions', methods=['GET'])
def show_group_auditions():
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
