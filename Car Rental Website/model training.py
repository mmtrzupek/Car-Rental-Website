#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import json
import pickle
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import json

df_trip = pd.read_csv('car_trip_history.csv')
df_trip = df_trip.dropna(subset=['price'])
df_car = pd.read_csv('car_details.csv')
df_car_trips = pd.merge(left = df_car, right = df_trip, how='inner', on='car_id')
df_car_trips = df_car_trips[['car_lat', 'car_lon', 'model', 'year', 'pickup_datetime', 'dropoff_datetime', 'price']]


with open("car_model_categ.json", "r") as f:
    data = json.load(f)

df_car_trips.model = df_car_trips['model'].map(data[0])

df_car_trips.model = df_car_trips.model.fillna(df_car_trips.model.mean())

df_car_trips.model = df_car_trips.model.astype(float)

df_car_trips['duration'] = pd.to_datetime(df_car_trips['dropoff_datetime']) - pd.to_datetime(df_car_trips['pickup_datetime'])
df_car_trips['duration'] = df_car_trips['duration'].dt.total_seconds()/60
df_car_trips.drop(['pickup_datetime', 'dropoff_datetime'], axis=1, inplace=True)
df_car_trips[np.isnan(df_car_trips.model)]['model']
df_car_trips.replace([np.inf, -np.inf], np.nan, inplace=True)
df_car_trips = df_car_trips.loc[(df_car_trips.duration >0) & (df_car_trips.duration <600)]

X = df_car_trips.loc[:, ['car_lat', 'car_lon', 'model', 'year', 'duration']]
y = df_car_trips.loc[:, ['price']]

regr = LinearRegression()
regr.fit(X, y)
regr.score(X, y)

# import the regressor
from sklearn.tree import DecisionTreeRegressor

# create a regressor object
regressor = DecisionTreeRegressor(random_state = 0)

# fit the regressor with X and Y data
regressor.fit(X, y)
regressor.score(X,y)

import xgboost
from xgboost import XGBRegressor
# create a regressor object
sgd = XGBRegressor(random_state = 0)

# fit the regressor with X and Y data
sgd.fit(X, y)
print(sgd.score(X,y))

# import the regressor
from sklearn.ensemble import RandomForestRegressor

# create a regressor object
rf = RandomForestRegressor(random_state = 0)

# fit the regressor with X and Y data
rf.fit(X, y)
print(rf.score(X,y))

filename = 'model.sav'
pickle.dump(regressor, open(filename, 'wb'))