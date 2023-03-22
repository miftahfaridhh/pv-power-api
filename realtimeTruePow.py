import schedule
import time
import threading
import mysql.connector

import mariadb

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
    # row = cur.fetchall()
    # print(row)
    # for i in range(len(row)):
    #     val = (str(row[i][0]), row[i][1])
    #     print(val)
    #     inserTruePow(val)
        # for j in range(len(row[i])):
        #     print(i, j, row[i][j])

    val = (str(row[0]), row[1])
    inserTruePow(val)
    # print("Raw : ", row,str(row[0]), row[1], val)
    cur.close()
    conn.close()
        
def truePower():
    threading.Thread(target=treadTruePow, args=()).start()

# run code every minute at xx:xx:00 second
schedule.every().minute.at(':00').do(truePower)

# run code every hour at xx:00:xx minute
# schedule.every().hour.at(':00').do(truePower)

while True:
    schedule.run_pending()
    time.sleep(.1)