from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

import mariadb
import threading
import mysql.connector
scheduler = BackgroundScheduler(daemon=True)


def inserTruePow(inputvalue):
    db_conn = mariadb.connect(host="113.198.211.94", user="abc", password="123", database="PVPowerGeneration", port=3360)
    db_cursor = db_conn.cursor()
    sqlCommand = "INSERT INTO `TruePow`(`D_date`, `F_all_power`) VALUES (%s, %s)"
    db_cursor.execute(sqlCommand,inputvalue) 
    db_conn.commit()
    # print(db_cursor.rowcount, "record inserted.")
    db_cursor.close()
    db_conn.close()

def treadTruePow():
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
    # print("Raw : ", row,str(row[0]), row[1], val)
    inserTruePow(val)
    cur.close()
    conn.close()
        
def truePower():
    threading.Thread(target=treadTruePow, args=()).start()


scheduler.start()
triggerTruePow = CronTrigger(second=0)
jobTruePow = scheduler.add_job(truePower,triggerTruePow)