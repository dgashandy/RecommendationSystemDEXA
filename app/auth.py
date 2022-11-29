from functools import wraps
from flask import current_app as app, g, Blueprint, jsonify, make_response, redirect, request, url_for
from flask_bcrypt import Bcrypt
import uuid
import json
import os

authAPI = Blueprint("auth", __name__)
bcrypt = Bcrypt()

def verifyLogin(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    token = request.cookies.get('token')
    g.user = None
    if (token == None):
      g.user = None
      return f(*args, **kwargs)
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    with open('accounts.json', 'r') as json_file:
      accounts = json.load(json_file)["accounts"]
      g.user = next((user for user in accounts if user["token"] == token), None)
      return f(*args, **kwargs)
  return wrap

def requireLogin(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if (g.user == None):
      return redirect('/login')
    else:
      return f(*args, **kwargs)
  return wrap

def requireAdmin(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if (g.user.role != 'admin'):
      return redirect('/')
    else:
      return f(*args, **kwargs)
  return wrap

@authAPI.route('/login', methods=['POST'])
def loginHandler():
  username = request.form.get('username')
  password = request.form.get('password')
  os.chdir(os.path.dirname(os.path.realpath(__file__)))
  with open('accounts.json', 'r') as json_file:
    accounts = json.load(json_file)["accounts"]
    index = next((i for i, acc in enumerate(accounts) if acc["username"] == username), -1)
    if (index == -1):
      return jsonify({ 'message': 'User not registered', 'data': False }), 400
    if (bcrypt.check_password_hash(accounts[index]["hashedPassword"], password) == False):
      return jsonify({ 'message': 'Incorrect password', 'data': False }), 400
    token = str(uuid.uuid1())
    accounts[index]["token"] = token
  with open('accounts.json', 'w') as json_file:
    json.dump({ "accounts": accounts }, json_file)
    #res = make_response(jsonify({ 'message': 'Login Success', 'data': True }))
    res = make_response(redirect('/'))
    res.set_cookie('token', token)
    return res

@authAPI.route('/logout')
@verifyLogin
def logoutHandler():
  if not (g.user):
    return redirect('/')
  os.chdir(os.path.dirname(os.path.realpath(__file__)))
  with open('accounts.json', 'r') as json_file:
    accounts = json.load(json_file)["accounts"]
    index = next((i for i, acc in enumerate(accounts) if acc["token"] == g.user["token"]), -1)
    if (index == -1):
      return jsonify({ 'message': 'User not logged in', 'data': False }), 400
    accounts[index]["token"] = ""
  with open('accounts.json', 'w') as json_file:
    json.dump({ "accounts": accounts }, json_file)
    res = make_response(redirect('/login'))
    res.set_cookie('token', '', 0, httponly=True)
    return res

@authAPI.route('/register', methods=['POST'])
def registerHandler():
  newUser = {
    'username': request.form.get('username'),
    'hashedPassword': bcrypt.generate_password_hash(request.form.get('password'), 10).decode('utf-8'),
    'name': request.form.get('name'),
    'role': 'user',
    'token': ''
  }
  os.chdir(os.path.dirname(os.path.realpath(__file__)))
  with open('accounts.json', 'r') as json_file:
    accounts = json.load(json_file)["accounts"]
    index = next((i for i, acc in enumerate(accounts) if acc["username"] == newUser["username"]), -1)
    if (index == -1):
      accounts.append(newUser)
      with open('accounts.json', 'w') as json_file:
        json.dump({ "accounts": accounts }, json_file)
        #return jsonify({ "message": "User registered successfully", "data": True }), 201
        return redirect('/login')
    return jsonify({ "message": "User already registered", "data": False }), 403