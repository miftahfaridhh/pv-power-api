import mysql.connector
import mysql.connector as mariadb
from datetime import date, timedelta, datetime

def update_KMA():
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
        print("inputValue",inputValue)

def truePower():
    conn = mysql.connector.connect(
        host="ens-datacenter.kr",
        port="3306",
        user="kookmin",
        password="kookmin",
        database="ens_datacenter",
    )
    cur = conn.cursor()
    cur.execute("SELECT D_date, F_tot FROM tbl_pv_power WHERE C_scode = 717800003 GROUP BY DATE(D_date),HOUR(D_date) ORDER BY `tbl_pv_power`.`D_date` DESC LIMIT 1;")
    row = cur.fetchone()
    val = (str(row[0]), row[1])
    # print("Raw : ", row)
    print("Raw : ", row,str(row[0]), row[1], val)
    # inserTruePow(val)
    cur.close()
    conn.close()

truePower()