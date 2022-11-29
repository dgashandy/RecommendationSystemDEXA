from flask import Flask, g, request, render_template, jsonify, send_from_directory
#from flask_mysqldb import MySQL
from app import app, controllers, auth
import json
#import locale
#import os

#mysql = MySQL(app)
#app.mysql = mysql
app.static_folder = 'static'
app.register_blueprint(auth.authAPI, url_prefix='/auth')

@app.route('/')
@auth.verifyLogin
@auth.requireLogin
def handleHomepage():
  return render_template('Index.html', userData = g.user)
  #return send_from_directory(app.static_folder, 'index.html')

@app.route('/login', methods=['GET'])
def handleLoginPage():
  return render_template('Login.html')

@app.route('/register', methods=['GET'])
def handleRegisterPage():
  return render_template('Register.html')

@app.route('/weathermap', methods=['GET'])
@auth.verifyLogin
@auth.requireLogin
def handleWeatherMap():
  relasiData = controllers.getRelasiData()
  return render_template('WeatherMap.html', userData = g.user, relasiData = relasiData, dumpJson = json.dumps)

# @app.route('/relasi', methods=['POST'])
# def handleRelasi():
#   return jsonify(controllers.getRelasiData())

@app.route('/recommendation', methods=['POST'])
def handleRecommendation():
  #jsonData = request.get_json(force=True)
  relasiId = request.json.get('relasiId')
  #print(type(relasiId))
  relasiData, recommendationData = controllers.getRecommendation(relasiId)
  return jsonify({ "relasi": relasiData, "recommendation": recommendationData })
  #return render_template('ProductDetails.html', data = results)

@app.route('/<path:filename>')
def handleSendPage(filename):
  return send_from_directory(app.static_folder, filename)