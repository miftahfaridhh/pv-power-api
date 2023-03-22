import mariadb
import pandas as pd
import numpy as np
from datetime import datetime
from datetime import date, timedelta
import joblib
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import Sequential, layers
from tensorflow.keras.layers import Dense, LSTM, Dropout, Bidirectional, Input, Conv1D
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.losses import MeanSquaredError as MSELoss
from tensorflow.keras.metrics import MeanAbsolutePercentageError as MAPEMetrics
from tensorflow.keras.metrics import MeanAbsoluteError as MAEMetrics
from tensorflow.keras.metrics import MeanSquaredError as MSEMetrics
import tensorflow_addons as tfa

def create_model(units):
    model = Sequential()
    model.add(Input(shape=(24, 8)))
    model.add(Bidirectional(LSTM(units = units, return_sequences=True)))
    model.add(Bidirectional(LSTM(units = 24),merge_mode='sum'))

    model.compile(optimizer=tf.keras.optimizers.Adam(0.001),
                loss=tf.keras.losses.MeanSquaredError(),
                metrics=[MAEMetrics(), MSEMetrics(), MAPEMetrics(), tf.nn.log_poisson_loss, tfa.metrics.RSquare()])
    return model
    
def prediction(model, iteration, X_test):
    prediction = model.predict(X_test)
    return prediction

def predict():

    station_ids = [108,105,133,235,239,127,112,202,156,165,146,159,253,152,184,143,283]
    # station_ids = [283]
    locations = ['서울', '강원', '대전', '충남', '세종', '충북', '인천', '경기', '광주', '전남', '전북', '부산', '경남', '울산', '제주', '대구', '경주']
    # METHOD_NAME = ['BiLSTM','BiLSTM_SingleDense','BiLSTM_MultiDense','Conv_LSTM','LSTM','RNN']
    METHOD_NAME = ['BiLSTM','Conv_LSTM','LSTM','RNN']

    for j in (station_ids):
        for k in (METHOD_NAME):
            # print(j,k)
            db_conn = mariadb.connect(host="113.198.211.94", user="abc", password="123", database="PVPowerGeneration", port=3360)
            db_cursor = db_conn.cursor()

            stationID = 283
            dateNow = '2023-02-15'
            db_command = f"SELECT * FROM WeatherDataKMA WHERE stationID = {j} AND DATE(dataDatetime) = '{dateNow}'"
            db_cursor.execute(db_command)
            response = db_cursor.fetchall()

            db_cursor.close()
            db_conn.close()

            print(response)

            df = pd.DataFrame(response, columns=['time','sId','sName','temperature','precipitation','ws','wd','humidity','daylight','solarRadiation','totalCloudCover'])

            df_ws = df.pop('ws')
            df_wd_rad = df.pop('wd')*np.pi/180

            df['wx'] = df_ws * np.cos(df_wd_rad)
            df['wy'] = df_ws * np.sin(df_wd_rad)

            df = df.drop(['time','sId','sName'],axis=1)

            print(df.describe())

            df = df[['temperature','precipitation','wx','wy','humidity','daylight','solarRadiation','totalCloudCover']]

            fitted_mm = joblib.load('minmax.pkl')
            fit_pow = joblib.load('minmaxpow.pkl')

            norm_df = fitted_mm.transform(df)

            print(norm_df.shape)
            norm_df = norm_df.reshape(1,24,8)

            model_build = create_model(24)

            checkpointFolder = 'all_train_data/train_artifacts'
            # METHOD_NAME = 'BiLSTM'
            PURPOSE = 'PVPowerGeneration'
            PRED_LENGTH = '24Hours'
            train_filename = '24h_sklearn_minmax_train.pkl'
            TRAIN_NAME = f'{k}-{PURPOSE}-{PRED_LENGTH}-{train_filename}'

            checkpoint_path = f'{checkpointFolder}/{TRAIN_NAME}'

            model_build.load_weights(checkpoint_path)

            prediction_result = prediction(model_build,10,norm_df)

            # pred = prediction_result
            print(prediction_result.shape)
            print(prediction_result)

            pred = np.empty(shape=(1,24))

            for l in range(24):
                pred_std = (prediction_result[0][l] - (-1)) / (1 - (-1))
                pred[0][l] = (pred_std * (99-0)) + 0

            print(pred)

            datenext = datetime.strptime(dateNow, '%Y-%m-%d') + timedelta(hours=1)
            print(datenext)
            print(datenext + timedelta(hours=1))

            db_conn = mariadb.connect(host="113.198.211.94", user="abc", password="123", database="PVPowerGeneration", port=3360)
            db_cursor = db_conn.cursor()

            datenext = datetime.strptime(dateNow, '%Y-%m-%d')
            for m in range(24):
                sqlKMA = f"INSERT IGNORE INTO PredictionResult (dataDatetime,stationID,stationName,modelAI,prediction)\
                        VALUES ('{datenext}', {283}, '{j}', '{k}', {pred[0][m]})"
                db_cursor.execute(sqlKMA) 
                db_conn.commit()

                datenext = datenext + timedelta(hours=1)

            db_cursor.close()
            db_conn.close()

if __name__ == '__main__':
    predict()