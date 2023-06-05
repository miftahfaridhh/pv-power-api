from flask import Flask, render_template
from flask_restful import Resource, Api, reqparse
import pandas as pd
import numpy as np
from datetime import datetime
from datetime import date, timedelta
import joblib
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import Sequential, layers
from tensorflow.keras.layers import Dense, LSTM, Dropout, Bidirectional, Input, Conv1D, SimpleRNN
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.losses import MeanSquaredError as MSELoss
from tensorflow.keras.metrics import MeanAbsolutePercentageError as MAPEMetrics
from tensorflow.keras.metrics import MeanAbsoluteError as MAEMetrics
from tensorflow.keras.metrics import MeanSquaredError as MSEMetrics
import tensorflow_addons as tfa

from flask import Flask
from flask_apscheduler import APScheduler
import time
import requests
import json

import threading
import mysql.connector
import mysql.connector as mariadb

from datetime import date, timedelta, datetime

# def post_data_kma(inputValue):
#     db_conn = mariadb.connect(host="113.198.211.94", user="abc", password="123", database="PVPowerGeneration", port=3360)
#     db_cursor = db_conn.cursor()
#     sqlKMA = 'INSERT INTO `weatherdataENS`(`C_scode`, `D_date`, `I_dev`, `I_comyn`, `F_temp`, `F_humidity`, `F_wind_direction`, `F_wind_speed`, `F_percipitation`, `F_insolation_slope`, `F_insolation_horizon`, `F_atmosp_press`, `F_dewpoint`, `F_dat1`, `F_dat2`, `F_dat3`, `F_dat4`, `F_dat5`)\
#          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
#     db_cursor.execute(sqlKMA,inputValue) 
#     db_conn.commit()
#     # print(db_cursor.rowcount, "record inserted.")
#     db_cursor.close()
#     db_conn.close()

# def update_KMA():
#     conn = mysql.connector.connect(
#         host="ens-datacenter.kr",
#         port="3306",
#         user="kmsg22",
#         password="kmsg22",
#         database="ens_datacenter",
#     )
#     cur = conn.cursor()
#     cur.execute("SELECT * FROM tbl_weather_dat WHERE C_scode = 717804001 AND D_date BETWEEN '2023-06-04 10:00:00' AND '2023-06-05 10:00:00' GROUP BY DATE(D_date),HOUR(D_date) ORDER BY `tbl_weather_dat`.`D_date`")
#     row = cur.fetchall()
#     cur.close()
#     conn.close()

#     for i in range (len(row)):
#         inputValue = []
#         for j in range (len(row[i])):
#             inputValue.append(row[i][j])    
#         # print(inputValue)
#         post_data_kma(inputValue)



# dateTday = datetime.now().date()
# dateYst = (dateTday - timedelta(days=1))
# dateYstt = (dateTday - timedelta(days=2))
# dateYst = dateYst.strftime('%Y-%m-%d')

# print(dateYst)

# db_conn = mariadb.connect(host="113.198.211.94", user="abc", password="123", database="PVPowerGeneration", port=3360)
# db_cursor = db_conn.cursor()

# dateToday = datetime.now().date().strftime('%Y%m%d')
# print(dateToday)

# dateTday = datetime.now().date()
# dateYst = (dateTday - timedelta(days=1)).strftime('%Y-%m-%d')
# dateYstt = (dateTday - timedelta(days=2)).strftime('%Y-%m-%d')
# dateTday = dateTday.strftime('%Y-%m-%d')

# db_command = f"SELECT * FROM weatherdataENS WHERE D_date BETWEEN '{dateYst} 10:00:00' AND '{dateTday} 10:00:00' GROUP BY DATE(D_date),HOUR(D_date) ORDER BY 'D_date' ASC"
# db_cursor.execute(db_command)
# response = db_cursor.fetchall()

# db_cursor.close()
# db_conn.close()

# print(response)

# df = pd.DataFrame(response, columns=['D_date','I_comyn','F_temp','F_humidity','F_wind_direction','F_wind_speed',
#                                         'F_precipitation','F_insolation_slope','F_insolation_horizon','F_atmosp_press',
#                                         'F_dewpoint','F_dat1', 'F_dat2', 'F_dat3', 'F_dat4', 'F_dat5'])
# df = df.rename(columns={'D_date':'DateTime','I_comyn':'Communication','F_temp':'Temperature','F_humidity':'Humidity',
#                         'F_wind_direction':'WindDirection','F_wind_speed':'WindSpeed','F_precipitation':'Precipitation',
#                         'F_insolation_slope':'InsolationSlope','F_insolation_horizon':'InsolationHorizon','F_atmosp_press':'AtmosphericPressure',
#                         'F_dewpoint':'DewPoint'})

# df['Temperature'] = pd.to_numeric(df['Temperature'])
# df['Humidity'] = pd.to_numeric(df['Humidity'])
# df['WindSpeed'] = pd.to_numeric(df['WindSpeed'])
# df['InsolationSlope'] = pd.to_numeric(df['InsolationSlope'])
# df['InsolationHorizon'] = pd.to_numeric(df['InsolationHorizon'])

# print(df.describe())

# # df_ws = df.pop('WSD')
# # df_wd_rad = df.pop('VEC')

# # df_wd_rad = df_wd_rad*np.pi/180

# # df['wx'] = df_ws * np.cos(df_wd_rad)
# # df['wy'] = df_ws * np.sin(df_wd_rad)

# df = df.drop(['DateTime','Communication','WindDirection','Precipitation','AtmosphericPressure','DewPoint','F_dat1', 'F_dat2', 'F_dat3', 'F_dat4', 'F_dat5'],axis=1)

# print(df.describe())

# dateToday = datetime.now().date().strftime('%Y-%m-%d')
# dateYst = datetime.now().date().strftime('%Y-%m-%d') - timedelta(days=1)


def post_data_kma(inputValue):
    db_conn = mariadb.connect(host="113.198.211.94", user="abc", password="123", database="PVPowerGeneration", port=3360)
    db_cursor = db_conn.cursor()
    sqlKMA = 'INSERT INTO `weatherdataENS16`(`C_scode`, `D_date`, `I_dev`, `I_comyn`, `F_temp`, `F_humidity`, `F_wind_direction`, `F_wind_speed`, `F_percipitation`, `F_insolation_slope`, `F_insolation_horizon`, `F_atmosp_press`, `F_dewpoint`, `F_dat1`, `F_dat2`, `F_dat3`, `F_dat4`, `F_dat5`)\
         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    db_cursor.execute(sqlKMA,inputValue) 
    db_conn.commit()
    # print(db_cursor.rowcount, "record inserted.")
    db_cursor.close()
    db_conn.close()

def update_KMA():
    dateToday = datetime.now().date()
    dateYst = (dateToday - timedelta(days=1)).strftime('%Y-%m-%d')
    dateToday = dateToday.strftime('%Y-%m-%d')

    conn = mysql.connector.connect(
        host="ens-datacenter.kr",
        port="3306",
        user="kmsg22",
        password="kmsg22",
        database="ens_datacenter",
    )

    cur = conn.cursor()
    cur.execute(f"SELECT * FROM tbl_weather_dat WHERE C_scode = 717804001 AND D_date BETWEEN '{dateYst} 16:00:00' AND '{dateToday} 15:55:00' GROUP BY DATE(D_date),HOUR(D_date) ORDER BY `tbl_weather_dat`.`D_date` ASC")
    row = cur.fetchall()
    cur.close()
    conn.close()

    for i in range (len(row)):
        inputValue = []
        for j in range (len(row[i])):
            inputValue.append(row[i][j])    
        print(inputValue)
        post_data_kma(inputValue)

update_KMA()