import requests
import csv
import numpy as np
import ast
import os

relasiData = [
  ["Apotek Suka Sehat", "-1.118337", "119.910992"],
  ["Apotek Anti Sakit", "0.502068", "101.550157"],
  ["Apotek Sejahtera", "-2.097371", "114.016342"],
  ["Apotek Pogung Farma", "-7.795629", "110.380812"],
  ["Apotek Harapan Bangsa", "-3.286404", "128.489214"],
]

def getRelasiData():
  return relasiData

def getLocationParameter(lat, long):
  response = requests.get("http://dataservice.accuweather.com/locations/v1/cities/geoposition/search", headers={ 'Content-Type': 'application/json' }, params={"apikey": "wJ7BRhfOwzCc63u5zExI3bnAbz5L7Pl8", "q": str(lat)+","+str(long), "language":"id-id", "details":"false", "toplevel":"true"})
  #print(response.json())
  return response.json()["Key"], response.json()["AdministrativeArea"]["LocalizedName"]

def getWeatherParameter(locationKey):
  response = requests.get("http://dataservice.accuweather.com/forecasts/v1/daily/5day/"+locationKey, params={"apikey": "wJ7BRhfOwzCc63u5zExI3bnAbz5L7Pl8", "language":"en-us", "details":"true", "metric":"true"})
  daily_forecasts = response.json()["DailyForecasts"]
  sum_temp = 0
  for day in daily_forecasts:
    sum_temp += ((float(day["Temperature"]["Minimum"]["Value"]) + float(day["Temperature"]["Maximum"]["Value"]))/2.0)
  avg_temp = sum_temp / len(daily_forecasts)
  label = "panas" if (avg_temp >= 28.0) else "dingin"
  #label "panas" atau "dingin"
  return avg_temp, label

def getDemographyParameter(provinceName):
  with open(os.path.join(os.path.dirname(__file__), 'demography.csv'), 'r') as readData:
    dataset = np.array(list(csv.reader(readData)))
  dataset = dataset[1:, :]
  data = []
  for province in dataset:
    if (province[0] == provinceName):
      data = province[1:]
      break
  prefix_sum = []
  for age_group_freq in data:
    prefix_sum.append(float(age_group_freq) + float(prefix_sum[len(prefix_sum)-1] if len(prefix_sum) > 0 else 0))
  q1 = prefix_sum[len(prefix_sum)-1]/4
  q3 = prefix_sum[len(prefix_sum)-1]*(3/4)
  rangeL = 0
  while (q1 > prefix_sum[rangeL]):
    rangeL += 1
  rangeR = len(data)-1
  while (q3 < prefix_sum[rangeR]):
    rangeR -= 1
  if (q3 != prefix_sum[rangeR]):
    rangeR += 1
  # IQR usia
  rangeL = rangeL*5
  rangeR = (rangeR+1)*5
  rangeStr = str(rangeL) + ' - ' + str(rangeR)

  def checkBetween(left, right, value):
    return (left <= value and value <= right)

  leftGroup = -1
  rightGroup = -1
  if (checkBetween(0, 9, rangeL)):
    leftGroup = 0
  elif (checkBetween(10, 19, rangeL)):
    leftGroup = 1
  else:
    leftGroup = 2
  if (checkBetween(0, 9, rangeR)):
    rightGroup = 0
  elif (checkBetween(10, 19, rangeR)):
    rightGroup = 1
  else:
    rightGroup = 2
  return rangeStr, list(range(leftGroup, rightGroup+1))

def recommendationClusterSelection(relasi_id):
  with open(os.path.join(os.path.dirname(__file__), 'dataset_all.csv'), 'r', encoding='utf-8') as readData:
    dataset = np.array(list(csv.reader(readData)))
  dataset = dataset[1:, :]
  freq_per_cluster = {}
  for index, data in enumerate(dataset):
    if (data[-4] == str(relasi_id)):
      freq_per_cluster[data[-3]] =  freq_per_cluster[data[-3]] + 1 if data[-3] in freq_per_cluster else 1
  max_freq = freq_per_cluster[max(freq_per_cluster, key=freq_per_cluster.get)]
  cluster_index_selected = [cluster for cluster,freq in freq_per_cluster.items() if freq == max_freq]
  cluster_selected = []
  for index in cluster_index_selected:
    for data in dataset:
      if (data[-3] == index and data[-4] == '0'):
        cluster_selected.append(data)
  return np.array(cluster_selected)

def recommendationSelectionRank(cluster_selected, weather_label, demography_label):
  if (weather_label == 'dingin'):
    for index, data in enumerate(cluster_selected):
      cluster_selected[index, -2] = 2 - int(data[-2])

  cluster_selected = cluster_selected.tolist()
  for index, data in enumerate(cluster_selected):
    match_point = len(np.intersect1d(list(data[-1]), demography_label))
    cluster_selected[index].append(int(data[-2]) + match_point)
  
  cluster_selected = np.array(cluster_selected)
  cluster_ranked = cluster_selected[cluster_selected[:, -1].argsort()[::-1]]
  return cluster_ranked.tolist()

def getRecommendation(relasi_id):
  relasi = relasiData[int(relasi_id)-1]
  locationKey, provinceName = getLocationParameter(relasi[1], relasi[2])
  weatherTemp, weatherLabel = getWeatherParameter(locationKey)
  demographyStr, demographyLabel = getDemographyParameter(provinceName)

  relasi.append(provinceName)
  relasi.append(weatherLabel + ' (' + "{:.2f}".format(weatherTemp) + ' C)')
  relasi.append(demographyStr)

  cluster_selected = recommendationClusterSelection(relasi_id)
  cluster_ranked = recommendationSelectionRank(cluster_selected, weatherLabel, demographyLabel)
  return relasi, cluster_ranked