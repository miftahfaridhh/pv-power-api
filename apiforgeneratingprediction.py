import os
from dotenv import load_dotenv

load_dotenv()

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
import tensorflow as tf
# physical_devices = tf.config.list_physical_devices('GPU')
# tf.config.experimental.set_memory_growth(physical_devices[0], enable=True)


from flask import Flask
from flask_apscheduler import APScheduler
import time
import requests
import json

import threading
import mysql.connector
import mysql.connector as mariadb

# Database credentials from environment variables
PV_DB_HOST = os.getenv("PV_DB_HOST")
PV_DB_USER = os.getenv("PV_DB_USER")
PV_DB_PASSWORD = os.getenv("PV_DB_PASSWORD")
PV_DB_NAME = os.getenv("PV_DB_NAME")
PV_DB_PORT = int(os.getenv("PV_DB_PORT", 12360))

def create_model(MODEL_TYPE):
    data_features = 12
    lr = 1e-3
    in_seq_length = 24
    out_seq_length = 24
    n_sliding_steps = 24

    model = Sequential()
    model.add(Input(shape=(in_seq_length, data_features)))
    if (MODEL_TYPE =='BiLSTM'):
        model.add(Bidirectional(LSTM(units=in_seq_length*2, return_sequences=True)))
        model.add(Dropout(0.2))
        model.add(Bidirectional(LSTM(units=in_seq_length*2, return_sequences=True)))
        model.add(Dropout(0.2))
        model.add(Bidirectional(LSTM(units=out_seq_length), merge_mode='sum'))
        model.add(Dense(units=out_seq_length, activation='tanh'))
    elif (MODEL_TYPE =='BiLSTM_SingleDense'):
        model.add(Bidirectional(LSTM(units=in_seq_length, return_sequences=True)))
        model.add(Dropout(0.2))
        model.add(Bidirectional(LSTM(units=in_seq_length*5)))
        model.add(Dropout(0.2))
        model.add(Dense(units=256, activation='tanh'))
        model.add(Dropout(0.2))
        model.add(Dense(units=out_seq_length, activation='tanh'))
    elif (MODEL_TYPE =='BiLSTM_MultiDense'):
        model.add(Bidirectional(LSTM(units=in_seq_length, return_sequences=True)))
        model.add(Dropout(0.2))
        model.add(Bidirectional(LSTM(units=in_seq_length*5)))
        model.add(Dropout(0.2))
        model.add(Dense(units=500, activation='tanh'))
        model.add(Dropout(0.2))
        model.add(Dense(units=250, activation='tanh'))
        model.add(Dropout(0.2))
        model.add(Dense(units=out_seq_length, activation='tanh'))
    elif (MODEL_TYPE =='LSTM'):
        model.add(LSTM(units=in_seq_length, return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(units=in_seq_length*2, return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(units=out_seq_length))
        model.add(Dense(units=out_seq_length, activation='tanh'))
    elif (MODEL_TYPE =='ConvLSTM'):
        model.add(Conv1D(filters=128, kernel_size=3, padding='same', activation='tanh'))
        model.add(Dropout(0.2))
        model.add(Conv1D(filters=256, kernel_size=3, padding='same', activation='tanh'))
        model.add(Dropout(0.2))
        model.add(Conv1D(filters=128, kernel_size=3, padding='same', activation='tanh'))
        model.add(Dropout(0.2))
        model.add(LSTM(units=in_seq_length, return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(units=out_seq_length))
        model.add(Dense(units=out_seq_length, activation='tanh'))
    elif (MODEL_TYPE =='RNN'):
        model.add(SimpleRNN(units=in_seq_length*2, return_sequences=True))
        model.add(Dropout(0.2))
        model.add(SimpleRNN(units=in_seq_length*2, return_sequences=True))
        model.add(Dropout(0.2))
        model.add(SimpleRNN(units=out_seq_length))
        model.add(Dense(units=out_seq_length, activation='tanh'))
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=lr),
            loss=tf.keras.losses.MeanSquaredError(),
            metrics=[MAEMetrics(), MSEMetrics(), MAPEMetrics()])
    return model
    
def prediction(model, iteration, X_test):
    prediction = model.predict(X_test)
    return prediction

def predict(modeltimes, dateToday):
    SITE_NAMES = ['717800001','717800002','717800003','717800004','717800005','717800006','717800007', '717800008', '717800009', '717800010']
    
    # MODELTIMES = ['10', '16']
    MODELTIMES = [str(modeltimes)]
    METHOD_NAMES =  ['BiLSTM', 'BiLSTM_SingleDense', 'BiLSTM_MultiDense', 'LSTM', 'ConvLSTM', 'RNN']
    for SITE_NAME in (SITE_NAMES):
        for MODELTIME in (MODELTIMES):
            for METHOD_NAME in (METHOD_NAMES):
                # print(j,METHOD_NAME)
                db_conn = mariadb.connect(host=PV_DB_HOST, user=PV_DB_USER, password=PV_DB_PASSWORD, database=PV_DB_NAME, port=PV_DB_PORT)
                db_cursor = db_conn.cursor()

                # dateToday = datetime.now().date()
                # print(dateToday)

                # dateTday = datetime.now().date()
                dateYst = (dateToday - timedelta(days=1)).strftime('%Y-%m-%d')
                dateYstt = (dateToday - timedelta(days=2)).strftime('%Y-%m-%d')
                dateTday = dateToday.strftime('%Y-%m-%d')
                print("=== Prediction at ",dateTday, " For predicting next day power generation ===")

                db_command = f"SELECT * FROM tbl_kma_weather WHERE D_date BETWEEN '{dateYst} 00:00:00' AND '{dateYst} 23:00:00' GROUP BY DATE(D_date),HOUR(D_date) ORDER BY 'D_date' ASC"
                db_cursor.execute(db_command)
                response = db_cursor.fetchall()

                # print(response)

                db_cursor.close()
                db_conn.close()

                # print(response)

                df_raw = pd.DataFrame(response, columns=['C_scode','D_date','F_30cm_soil_temp','F_20cm_soil_temp','F_10cm_soil_temp','F_5cm_soil_temp','F_ground_temp','F_dmst_mtph_no','F_ground_state','C_visibility','F_min_cloud_cover','C_cloud_pattern','F_mid_low_cloud_cover','F_total_cloud_cover','F_3hr_snowfall','F_snowfall','F_solar_radiation','F_daylight','F_sea_level_pressure','F_local_pressure','F_dew_point_temp','F_vapor_pressure','F_humidity','F_wind_direction','F_wind_speed','F_precipitation','F_temp'])

                df = df_raw[['F_10cm_soil_temp', 'F_5cm_soil_temp',
                            'F_ground_temp', 'C_visibility', 'F_min_cloud_cover',
                            'F_mid_low_cloud_cover', 'F_total_cloud_cover', 'F_solar_radiation',
                            'F_daylight', 'F_humidity', 'F_wind_speed', 'F_temp']]
                

                # Mengubah tipe data kolom menjadi numerik
                numeric_columns = [
                    'F_10cm_soil_temp', 'F_5cm_soil_temp', 'F_ground_temp', 'C_visibility', 'F_min_cloud_cover',
                    'F_mid_low_cloud_cover', 'F_total_cloud_cover', 'F_solar_radiation', 'F_daylight', 
                    'F_humidity', 'F_wind_speed', 'F_temp'
                ]

                for col in numeric_columns:
                    df.loc[:, col] = pd.to_numeric(df[col], errors='coerce')

                
                if MODELTIME == '10' :
                    checkpointFolder = f'train_data'

                    if SITE_NAME == '717800001':
                        MINDATA = 0
                        MAXDATA = 82.0

                    elif SITE_NAME == '717800002':
                        MINDATA = 0
                        MAXDATA = 83.0

                    elif SITE_NAME == '717800003':
                        MINDATA = 0
                        MAXDATA = 86.0

                    elif SITE_NAME == '717800004':
                        MINDATA = 0
                        MAXDATA = 86.0

                    elif SITE_NAME == '717800005':
                        MINDATA = 0
                        MAXDATA = 86.0
                    
                    elif SITE_NAME == '717800006':
                        MINDATA = 0
                        MAXDATA = 38.90999999997439

                    elif SITE_NAME == '717800007':
                        MINDATA = 0
                        MAXDATA = 41.14999999999418

                    elif SITE_NAME == '717800008':
                        MINDATA = 0
                        MAXDATA = 41.01000000000931

                    elif SITE_NAME == '717800009':
                        MINDATA = 0
                        MAXDATA = 40.0800000000163
                    
                    elif SITE_NAME == '717800010':
                        MINDATA = 0
                        MAXDATA = 39.97000000000117
                
                elif MODELTIME == '16' :
                    checkpointFolder = f'train_data2021'

                    if SITE_NAME == '717800001':
                        MINDATA = 0
                        MAXDATA = 82.0

                    elif SITE_NAME == '717800002':
                        MINDATA = 0
                        MAXDATA = 84.0

                    elif SITE_NAME == '717800003':
                        MINDATA = 0
                        MAXDATA = 87.0

                    elif SITE_NAME == '717800004':
                        MINDATA = 0
                        MAXDATA = 86.0

                    elif SITE_NAME == '717800005':
                        MINDATA = 0
                        MAXDATA = 86.0
                    
                    elif SITE_NAME == '717800006':
                        MINDATA = 0
                        MAXDATA = 39.0

                    elif SITE_NAME == '717800007':
                        MINDATA = 0
                        MAXDATA = 41.14999999999418

                    elif SITE_NAME == '717800008':
                        MINDATA = 0
                        MAXDATA = 41.04000000000815

                    elif SITE_NAME == '717800009':
                        MINDATA = 0
                        MAXDATA = 40.0800000000163
                    
                    elif SITE_NAME == '717800010':
                        MINDATA = 0
                        MAXDATA = 39.97000000000117


                fitted_mm = joblib.load(f'{checkpointFolder}/{SITE_NAME}/minmaxShort.pkl')

                norm_df = fitted_mm.transform(df)

                print(norm_df.shape)
                norm_df = norm_df.reshape(1,24,12)

                model_build = create_model(METHOD_NAME)

                checkpoint_path = f'{checkpointFolder}/{SITE_NAME}/2/{METHOD_NAME}'

                model_build.load_weights(checkpoint_path)

                prediction_result = prediction(model_build,10,norm_df)

                pred = np.empty(shape=(1,24))

                ###### denorm process ###### 


                
                for l in range(24):
                    pred_std = (prediction_result[0][l] - (-1)) / (1 - (-1))
                    kkk = (pred_std * (MAXDATA-MINDATA)) + MINDATA
                    if l < 4 or l > 21 :
                        pred[0][l] = 0
                    else :
                        if (kkk) < 0:
                            pred[0][l] = 0
                        else :
                            pred[0][l] = kkk

                # print(pred)

                db_conn = mariadb.connect(host=PV_DB_HOST, user=PV_DB_USER, password=PV_DB_PASSWORD, database=PV_DB_NAME, port=PV_DB_PORT)
                db_cursor = db_conn.cursor()

                # datenext = dateToday + timedelta(days=1)
                datenext = dateToday
                print('START PREDICTING !!!!!!!!!!!!!!!', METHOD_NAME)
                for m in range(24):
                    # print('INSERT DATA TO DB', m)
                    datenextstr = datenext.strftime('%Y%m%d')
                    sqlKMA = f"INSERT IGNORE INTO  predictionresult(datename, modeltime, sitename, methodname, predictionvalue)\
                            VALUES ('{datenextstr}', {MODELTIME}, {SITE_NAME}, '{METHOD_NAME}', {pred[0][m]})"
                    db_cursor.execute(sqlKMA) 
                    db_conn.commit()
                    datenext += timedelta(hours=1)

                db_cursor.close()
                db_conn.close()
    print(f"======= Prediction Finished for {MODELTIMES} o'clock =======")


# Tanggal awal
tanggal_awal = datetime(2024, 7, 1).date()

# Tanggal sekarang
tanggal_sekarang = datetime(2024, 7, 7).date()
DATE_TODAYS = [tanggal_awal + timedelta(n) for n in range((tanggal_sekarang - tanggal_awal).days + 1)]

# MODELTIMES = ["1", "2"]
MODELTIMES = [ "10","16"]

for DATE_TODAY in (DATE_TODAYS):
    for MODELTIME in (MODELTIMES):
        predict(MODELTIME, DATE_TODAY)
