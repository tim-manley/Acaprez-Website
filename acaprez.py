#!/usr/bin/env python

#-----------------------------------------------------------------------
# acaprez.py
# Authors: Tim Manley
#-----------------------------------------------------------------------

from flask import Flask, request, make_response, redirect, url_for
from flask import render_template
from database import get_groups

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

@app.route('/auditionee', methods=['GET'])
def auditionee():

    groups = get_groups() # Exception handling ommitted

    html = render_template('auditionee.html', groups=groups)
    response = make_response(html)
    return response

#-----------------------------------------------------------------------

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
