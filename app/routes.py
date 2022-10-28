from flask import Flask, request, render_template, jsonify, send_from_directory
#from flask_mysqldb import MySQL
from app import app, controllers
#import locale
#import os

#mysql = MySQL(app)
#app.mysql = mysql
app.static_folder = 'static'

@app.route('/')
def handleHomepage():
  return send_from_directory(app.static_folder, 'index.html')

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