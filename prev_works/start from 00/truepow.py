from apscheduler.schedulers.background import BackgroundScheduler
from flask_restful import Api

import mariadb
import threading
import mysql.connector
from flask import Flask
from flask_apscheduler import APScheduler
import numpy as np

db_conn = mariadb.connect(host="113.198.211.94", user="abc", password="123", database="PVPowerGeneration", port=3360)
db_cursor = db_conn.cursor()
db_command2 = f"SELECT F_all_power FROM `TruePow` WHERE DATE(D_date) = 20230328"
db_cursor.execute(db_command2)
response2 = db_cursor.fetchall()

db_cursor.close()
db_conn.close()

print(response2, len(response2))

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

print(data2, len(data2))