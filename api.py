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
import tensorflow as tf
physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], enable=True)


from flask import Flask
from flask_apscheduler import APScheduler
import time
import requests
import json

import threading
import mysql.connector
import mysql.connector as mariadb

app = Flask(__name__)
api = Api(app)

scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()

parser = reqparse.RequestParser()
parser.add_argument('date')
parser.add_argument('sitecode')
parser.add_argument('model')
parser.add_argument('modeltime')

def create_model(units, modelName):
    if modelName == 'BiLSTM':
        model = Sequential()
        model.add(Input(shape=(24, 5)))
        model.add(Bidirectional(LSTM(units = units, return_sequences=True)))
        model.add(Bidirectional(LSTM(units = 24),merge_mode='sum'))

        model.compile(optimizer=tf.keras.optimizers.Adam(0.001),
                    loss=tf.keras.losses.MeanSquaredError(),
                    metrics=[MAEMetrics(), MSEMetrics(), MAPEMetrics(), tf.nn.log_poisson_loss, tfa.metrics.RSquare()])
        
    elif modelName == 'BiLSTM_MultiDense':
        model = Sequential()
        model.add(Input(shape=(24, 5)))
        model.add(Bidirectional(LSTM(units = units, return_sequences=True)))
        model.add(Bidirectional(LSTM(units = units*5)))
        
        model.add(Dense(units=500,activation='tanh'))
        model.add(Dense(units=250,activation='tanh'))
        model.add(Dense(units=24,activation='tanh'))

        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.01),
                    loss=tf.keras.losses.MeanSquaredError(),
                    metrics=[MAEMetrics(), MSEMetrics(), MAPEMetrics(), tf.nn.log_poisson_loss, tfa.metrics.RSquare()])
        
    elif modelName == 'BiLSTM_SingleDense':
        model = Sequential()
        model.add(Input(shape=(24, 5)))
        model.add(Bidirectional(LSTM(units = units, return_sequences=True)))
        model.add(Bidirectional(LSTM(units = units*5)))
        model.add(Dense(units=24,activation='tanh'))

        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                    loss=tf.keras.losses.MeanSquaredError(),
                    metrics=[MAEMetrics(), MSEMetrics(), MAPEMetrics(), tf.nn.log_poisson_loss, tfa.metrics.RSquare()])
    
    elif modelName == 'Conv_LSTM':
        model = Sequential()
        model.add(Input(shape=(24, 5)))
        model.add(Conv1D(filters=128,kernel_size=3,padding='same',activation='tanh'))
        model.add(Conv1D(filters=256,kernel_size=3,padding='same',activation='tanh'))
        model.add(LSTM(units = units, return_sequences=True))
        model.add(LSTM(units = 24))
    
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                    loss=tf.keras.losses.MeanSquaredError(),
                    metrics=[MAEMetrics(), MSEMetrics(), MAPEMetrics(), tf.nn.log_poisson_loss, tfa.metrics.RSquare()])
        
    elif modelName == 'LSTM':
        model = Sequential()
        model.add(Input(shape=(24, 5)))
        model.add(LSTM(units = units, return_sequences=True))
        model.add(LSTM(units = 24))

        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=24),
                    loss=tf.keras.losses.MeanSquaredError(),
                    metrics=[MAEMetrics(), MSEMetrics(), MAPEMetrics(), tf.nn.log_poisson_loss, tfa.metrics.RSquare()])
        
    elif modelName == 'RNN':
        model = Sequential()
        model.add(Input(shape=(24, 5)))
        model.add(SimpleRNN(units = units*2, return_sequences=True))
        model.add(SimpleRNN(units = 24))

        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                    loss=tf.keras.losses.MeanSquaredError(),
                    metrics=[MAEMetrics(), MSEMetrics(), MAPEMetrics(), tf.nn.log_poisson_loss, tfa.metrics.RSquare()])

    return model
    
def prediction(model, iteration, X_test):
    prediction = model.predict(X_test)
    return prediction

@scheduler.task('cron', id='prediction', minute='50', hour='9,15')
def predict():
    SITE_NAMES = ['717800003','717800006','717800007', '717800008', '717800009', '717800010']
    current_datetime = datetime.now()
    # Get the current hour
    current_hour = current_datetime.hour
    next_hour = current_datetime + timedelta(hours=1)
    get_next_hour = next_hour.hours

    # MODELTIMES = ['10', '16']
    MODELTIMES = [str(get_next_hour)]
    METHOD_NAMES = ['BiLSTM','BiLSTM_MultiDense','BiLSTM_SingleDense','Conv_LSTM','LSTM','RNN']
    for SITE_NAME in (SITE_NAMES):
        for MODELTIME in (MODELTIMES):
            for METHOD_NAME in (METHOD_NAMES):
                # print(j,METHOD_NAME)
                db_conn = mariadb.connect(host=PV_DB_HOST, user=PV_DB_USER, password=PV_DB_PASSWORD, database=PV_DB_NAME, port=PV_DB_PORT)
                db_cursor = db_conn.cursor()

                dateToday = datetime.now().date().strftime('%Y%m%d')
                # print(dateToday)

                # dateTday = datetime.now().date()
                dateYst = (dateToday - timedelta(days=1)).strftime('%Y-%m-%d')
                dateYstt = (dateToday - timedelta(days=2)).strftime('%Y-%m-%d')
                dateTday = dateToday.strftime('%Y-%m-%d')
                print(dateTday)

                db_command = f"SELECT * FROM weatherdataENS{MODELTIME} WHERE D_date BETWEEN '{dateYst} {MODELTIME}:00:00' AND '{dateTday} {MODELTIME}:00:00' GROUP BY DATE(D_date),HOUR(D_date) ORDER BY 'D_date' ASC"
                db_cursor.execute(db_command)
                response = db_cursor.fetchall()

                db_cursor.close()
                db_conn.close()

                print(response)

                df = pd.DataFrame(response, columns=['C_scode','D_date','I_dev','I_comyn','F_temp','F_humidity','F_wind_direction','F_wind_speed',
                                                    'F_precipitation','F_insolation_slope','F_insolation_horizon','F_atmosp_press',
                                                    'F_dewpoint','F_dat1', 'F_dat2', 'F_dat3', 'F_dat4', 'F_dat5'])
                df = df.rename(columns={'D_date':'DateTime','I_comyn':'Communication','F_temp':'Temperature','F_humidity':'Humidity',
                                        'F_wind_direction':'WindDirection','F_wind_speed':'WindSpeed','F_precipitation':'Precipitation',
                                        'F_insolation_slope':'InsolationSlope','F_insolation_horizon':'InsolationHorizon','F_atmosp_press':'AtmosphericPressure',
                                        'F_dewpoint':'DewPoint'})

                df['Temperature'] = pd.to_numeric(df['Temperature'])
                df['Humidity'] = pd.to_numeric(df['Humidity'])
                df['WindSpeed'] = pd.to_numeric(df['WindSpeed'])
                df['InsolationSlope'] = pd.to_numeric(df['InsolationSlope'])
                df['InsolationHorizon'] = pd.to_numeric(df['InsolationHorizon'])

                print(df.describe())

                df = df.drop(['C_scode','DateTime','I_dev','Communication','WindDirection','Precipitation','AtmosphericPressure','DewPoint','F_dat1', 'F_dat2', 'F_dat3', 'F_dat4', 'F_dat5'],axis=1)

                print(df.describe())

                df.columns = ['Temperature','Humidity','WindSpeed','InsolationSlope','InsolationHorizon']
                df = df[['Temperature','Humidity','WindSpeed','InsolationSlope','InsolationHorizon']]

                fitted_mm = joblib.load('minmaxShort.pkl')
                fit_pow = joblib.load('minmaxpowShort.pkl')

                norm_df = fitted_mm.transform(df)

                print(norm_df.shape)
                norm_df = norm_df.reshape(1,24,5)

                model_build = create_model(24, METHOD_NAME)

                checkpointFolder = f'all_train_data/{SITE_NAME}/{MODELTIME}/train_artifacts'
                # METHOD_NAME = 'BiLSTM'
                PURPOSE = 'PVPowerGeneration-Short'
                PRED_LENGTH = '24Hours'
                train_filename = '24h_sklearn_minmax_trainShort.pkl'
                TRAIN_NAME = f'{METHOD_NAME}-{PURPOSE}-{PRED_LENGTH}-{train_filename}'

                checkpoint_path = f'{checkpointFolder}/{TRAIN_NAME}'

                model_build.load_weights(checkpoint_path)

                prediction_result = prediction(model_build,10,norm_df)

                # pred = prediction_result
                print(prediction_result.shape)
                print(prediction_result)

                pred = np.empty(shape=(1,24))

                ###### denorm process ###### 

                if SITE_NAME == '717800003':
                    MINDATA = 0
                    MAXDATA = 99
                
                elif SITE_NAME == '717800006':
                    MINDATA = 0
                    MAXDATA = 42.37

                elif SITE_NAME == '717800007':
                    MINDATA = 0
                    MAXDATA = 45.07

                elif SITE_NAME == '717800008':
                    MINDATA = 0
                    MAXDATA = 45.23

                elif SITE_NAME == '717800009':
                    MINDATA = 0
                    MAXDATA = 43.65
                
                elif SITE_NAME == '717800010':
                    MINDATA = 0
                    MAXDATA = 44.55

                
                for l in range(24):
                    pred_std = (prediction_result[0][l] - (-1)) / (1 - (-1))
                    kkk = (pred_std * (MAXDATA-MINDATA)) + MINDATA
                    if l < 5 or l > 20 :
                        pred[0][l] = 0
                    else :
                        if (kkk) < 0:
                            pred[0][l] = 0
                        else :
                            pred[0][l] = kkk

                print(pred)

                db_conn = mariadb.connect(host=PV_DB_HOST, user=PV_DB_USER, password=PV_DB_PASSWORD, database=PV_DB_NAME, port=PV_DB_PORT)
                db_cursor = db_conn.cursor()

                datenext = dateToday + timedelta(days=1)
                print('START PREDICTING !!!!!!!!!!!!!!!', METHOD_NAME)
                for m in range(24):
                    print('INSERT DATA TO DB', m)
                    datenextstr = datenext.strftime('%Y%m%d')
                    sqlKMA = f"INSERT IGNORE INTO  predictionresult(datename, modeltime, sitename, methodname, predictionvalue)\
                            VALUES ('{datenextstr}', {MODELTIME}, {SITE_NAME}, '{METHOD_NAME}', {pred[0][m]})"
                    db_cursor.execute(sqlKMA) 
                    db_conn.commit()

                    # datenext = datenext + timedelta(hours=1)
                    datenext += timedelta(hours=1)

                db_cursor.close()
                db_conn.close()

def post_data_kma(inputValue, modeltime):
    db_conn = mariadb.connect(host=PV_DB_HOST, user=PV_DB_USER, password=PV_DB_PASSWORD, database=PV_DB_NAME, port=PV_DB_PORT)
    db_cursor = db_conn.cursor()
    if modeltime == 10 :
        sqlKMA = 'INSERT INTO `weatherdataENS10`(`C_scode`, `D_date`, `I_dev`, `I_comyn`, `F_temp`, `F_humidity`, `F_wind_direction`, `F_wind_speed`, `F_percipitation`, `F_insolation_slope`, `F_insolation_horizon`, `F_atmosp_press`, `F_dewpoint`, `F_dat1`, `F_dat2`, `F_dat3`, `F_dat4`, `F_dat5`)\
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    elif modeltime == 16 :
        sqlKMA = 'INSERT INTO `weatherdataENS16`(`C_scode`, `D_date`, `I_dev`, `I_comyn`, `F_temp`, `F_humidity`, `F_wind_direction`, `F_wind_speed`, `F_percipitation`, `F_insolation_slope`, `F_insolation_horizon`, `F_atmosp_press`, `F_dewpoint`, `F_dat1`, `F_dat2`, `F_dat3`, `F_dat4`, `F_dat5`)\
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    db_cursor.execute(sqlKMA,inputValue) 
    db_conn.commit()
    db_cursor.close()
    db_conn.close()

@scheduler.task('cron', id='getWeather', minute='40', hour='9')
def update_KMA_10():
    dateToday = datetime.now().date()
    dateYst = (dateToday - timedelta(days=1)).strftime('%Y-%m-%d')

    conn = mysql.connector.connect(
        host="ens-datacenter.kr",
        port="3306",
        user="kookmin",
        password="kookmin",
        database="ens_datacenter",
    )

    cur = conn.cursor()
    cur.execute(f"SELECT * FROM tbl_weather_dat WHERE C_scode = 717804001 AND D_date BETWEEN '{dateYst} 10:00:00' AND '{dateToday} 10:00:00' GROUP BY DATE(D_date),HOUR(D_date) ORDER BY `tbl_weather_dat`.`D_date` ASC")
    row = cur.fetchall()
    cur.close()
    conn.close()

    for i in range (len(row)):
        inputValue = []
        for j in range (len(row[i])):
            inputValue.append(row[i][j])    
        # print(inputValue)
        # print("inputValue",inputValue)
        post_data_kma(inputValue, 10)
    print("Update Weather Data")

@scheduler.task('cron', id='getWeather', minute='40', hour='15')
def update_KMA_16():
    dateToday = datetime.now().date()
    dateYst = (dateToday - timedelta(days=1)).strftime('%Y-%m-%d')

    conn = mysql.connector.connect(
        host="ens-datacenter.kr",
        port="3306",
        user="kookmin",
        password="kookmin",
        database="ens_datacenter",
    )

    cur = conn.cursor()
    cur.execute(f"SELECT * FROM tbl_weather_dat WHERE C_scode = 717804001 AND D_date BETWEEN '{dateYst} 16:00:00' AND '{dateToday} 16:00:00' GROUP BY DATE(D_date),HOUR(D_date) ORDER BY `tbl_weather_dat`.`D_date` ASC")
    row = cur.fetchall()
    cur.close()
    conn.close()

    for i in range (len(row)):
        inputValue = []
        for j in range (len(row[i])):
            inputValue.append(row[i][j])
        post_data_kma(inputValue, 16)
    print("Update Weather Data")

# def inserTruePow(inputvalue):
#     db_conn = mariadb.connect(host=PV_DB_HOST, user=PV_DB_USER, password=PV_DB_PASSWORD, database=PV_DB_NAME, port=PV_DB_PORT)
#     db_cursor = db_conn.cursor()
#     sqlCommand = "INSERT INTO `TruePow`(`D_date`, `F_all_power`) VALUES (%s, %s)"
#     db_cursor.execute(sqlCommand,inputvalue) 
#     db_conn.commit()
#     # print(db_cursor.rowcount, "record inserted.")
#     db_cursor.close()
#     db_conn.close()

# @scheduler.task('cron', id='getTruePower', minute='10', hour='*')
# def truePower():
#     conn = mysql.connector.connect(host=ENS_DB_HOST, port=ENS_DB_PORT, user=ENS_DB_USER, password=ENS_DB_PASSWORD, database=ENS_DB_NAME)
#     cur = conn.cursor()
#     cur.execute("SELECT D_date, F_tot FROM tbl_pv_power WHERE C_scode = 717800003 GROUP BY DATE(D_date),HOUR(D_date) ORDER BY `tbl_pv_power`.`D_date` DESC LIMIT 1;")
#     row = cur.fetchone()
#     val = (str(row[0]), row[1])
#     # print("Raw : ", row)
#     print("Raw : ", row,str(row[0]), row[1], val)
#     # inserTruePow(val)
#     cur.close()
#     conn.close()

class getPrediction(Resource):
    def post(self):
        args = parser.parse_args()
        print(args['date'],args['sitecode'],args['model'],{args['modeltime']}, time.time())

        db_conn = mariadb.connect(host=PV_DB_HOST, user=PV_DB_USER, password=PV_DB_PASSWORD, database=PV_DB_NAME, port=PV_DB_PORT)
        db_cursor = db_conn.cursor()
        db_command = f"SELECT predictionValue FROM predictionresult WHERE sitename = {int(args['sitecode'])} AND \
            DATE(datename) = {int(args['date'])} AND methodname = '{args['model']}' AND modeltime = '{args['modeltime']}' ORDER BY `datename` ASC"
        # print(db_command)
        db_cursor.execute(db_command)
        response = db_cursor.fetchall()
        db_cursor.close()
        db_conn.close()

        conn = mysql.connector.connect(host=ENS_DB_HOST, port=ENS_DB_PORT, user=ENS_DB_USER, password=ENS_DB_PASSWORD, database=ENS_DB_NAME)
        cur = conn.cursor()
        cur.execute(f"SELECT F_tot FROM tbl_pv_power WHERE date(D_date) = {int(args['date'])} AND C_scode = {int(args['sitecode'])} GROUP BY DATE(D_date),HOUR(D_date)")
        response2 = cur.fetchall()
        # print("Raw Power : ", response2)
        cur.close()
        conn.close()

        sumPower = 0
        listData = []
        for qq in range(5,20):
            if not response:
                sumPower += np.array(float(0))
                kk = np.array(float(0))
            else:
                sumPower += float(response[qq][0])
                kk = np.array(float(response[qq][0]))
            listData.append(np.around(kk, 2))

        sumPower = np.around(sumPower,2)

        data2 = []
        sumPower2 = 0
        for qq in range(5,20):
            if qq < len(response2):
                sumPower2 += float(abs(response2[qq][0] - response2[qq-1][0]))
                kk = np.array(float(abs(response2[qq][0] - response2[qq-1][0])))
            else :
                sumPower2 += np.array(float(0))
                kk = np.array(float(0))
            data2.append(int(np.around(kk, 2)))
        
        errRate = str(round((abs(sumPower-sumPower2)/sumPower2*100),2))+"%"

        pred = {"type": "예측",
                        "hr5": listData[0],
                        "hr6": listData[1],
                        "hr7": listData[2],
                        "hr8": listData[3],
                        "hr9": listData[4],
                        "hr10": listData[5],
                        "hr11": listData[6],
                        "hr12": listData[7],
                        "hr13": listData[8],
                        "hr14": listData[9],
                        "hr15": listData[10],
                        "hr16": listData[11],
                        "hr17": listData[12],
                        "hr18": listData[13],
                        "hr19": listData[14],
                        "sum": sumPower,
                        "erRate": errRate}
        true = {"type": "진실",
                        "hr5": data2[0],
                        "hr6": data2[1],
                        "hr7": data2[2],
                        "hr8": data2[3],
                        "hr9": data2[4],
                        "hr10": data2[5],
                        "hr11": data2[6],
                        "hr12": data2[7],
                        "hr13": data2[8],
                        "hr14": data2[9],
                        "hr15": data2[10],
                        "hr16": data2[11],
                        "hr17": data2[12],
                        "hr18": data2[13],
                        "hr19": data2[14],
                        "sum": sumPower2,
                        "erRate": "-"}

        json_response =  {'pred':pred, 'true':true}

        # print(json_response)

        json_response = json.dumps(json_response)


        return {'data': json_response}

api.add_resource(getPrediction, '/data/api/powerpred')

@app.route('/')
def predPlot():
    return render_template('powerPlot.html')

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=5005,use_reloader=False)