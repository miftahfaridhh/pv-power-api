from apscheduler.schedulers.background import BackgroundScheduler
from flask_restful import Api

import mariadb
import threading
import mysql.connector
from flask import Flask
from flask_apscheduler import APScheduler

scheduler = BackgroundScheduler(daemon=True)
app = Flask(__name__)
api = Api(app)

scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()


# def inserTruePow(inputvalue):
#     db_conn = mariadb.connect(host="113.198.211.94", user="abc", password="123", database="PVPowerGeneration", port=3360)
#     db_cursor = db_conn.cursor()
#     sqlCommand = "INSERT INTO `TruePow`(`D_date`, `F_all_power`) VALUES (%s, %s)"
#     db_cursor.execute(sqlCommand,inputvalue) 
#     db_conn.commit()
#     print(db_cursor.rowcount, "record inserted.")
#     db_cursor.close()
#     db_conn.close()

@scheduler.task('cron', id='getTruePower', second='0')
def truePower():
    conn = mysql.connector.connect(
        host="kmsg007.iptime.org",
        port="3306",
        user="kmsg22",
        password="kmsg22",
        database="kmsg_inverter",
    )
    cur = conn.cursor()
    cur.execute("SELECT D_date, F_all_power FROM tbl_pvdat WHERE C_pcode = 71780003 ORDER BY `tbl_pvdat`.`D_date` DESC LIMIT 1;")
    row = cur.fetchone()
    val = (str(row[0]), row[1])
    print("Raw : ", row,str(row[0]), row[1], val)
    cur.close()
    conn.close()
    # inserTruePow(val)

if __name__ == "__main__":
    app.run(debug=False,host='localhost', port=5000)