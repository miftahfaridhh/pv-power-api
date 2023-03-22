import json
import requests
from datetime import date, timedelta
import pandas as pd
import numpy as np
import mariadb
from datetime import datetime
import time

max_request = 9995
curr_request = 1

def post_data_kma(inputvalue):
    db_conn = mariadb.connect(host="113.198.211.94", user="abc", password="123", database="PVPowerGeneration", port=3360)
    db_cursor = db_conn.cursor()
    sqlKMA = "INSERT IGNORE INTO WeatherDataKMA (dataDatetime,stationID,stationName,temperature,precipitation,windSpeed,windDirection,humidity,sunshineDuration,solarRadiation,cloudCover)\
         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    db_cursor.execute(sqlKMA,inputvalue) 
    db_conn.commit()
    print(db_cursor.rowcount, "record inserted.")
    db_cursor.close()
    db_conn.close()

def update_KMA(endHh,today_):
    if endHh<10:
        endHh = '0'+str(endHh)
    else:
        endHh = str(endHh)

    # today_ = date.today() - timedelta(1)
    # print(today_)
    today = str(today_).replace('-','')
    station_ids = [108,105,133,235,239,127,112,202,156,165,146,159,253,152,184,143,283]
    locations = ['서울', '강원', '대전', '충남', '세종', '충북', '인천', '경기', '광주', '전남', '전북', '부산', '경남', '울산', '제주', '대구', '경주']
    # endHr = datetime.now()
    # endHr = endHr.hour

    # today = '20220114'
    # print(today)

    # stationID = 283

    # # skey = "nC3ctBmHx40qp3D2SFEbCJBbR5MuRtuMLZW6+OVhn4xIQKoec9nhk2K9wyjXlyv4IYS1pYvtMeRIRRX0JI8Rkg=="
    skey = "sEKoH9gpdiVmk/am1yBhtISsAHaDs9hEbx8sPdz+hHDnrXoxmn9VDdJAvJdZcoxgdEXuNdav16beMDFszEQgLw=="
    url = 'https://apis.data.go.kr/1360000/AsosHourlyInfoService/getWthrDataList'
    json_data = []

    # params ={'serviceKey' : skey, 'pageNo' : '1', 'numOfRows ' : '1',
    #         'dataType' : 'JSON', 'dataCd' : 'ASOS', 'dateCd' : 'HR', 'startDt' : today,
    #         'startHh' : endHh, 'endDt' : today, 'endHh' : endHh, 'stnIds' : str(stationID) }
    # print(params)
    # response = requests.get(url, params=params, verify=False)
    # print(response.content)
    # json_data += json.loads(response.content)['response']['body']['items']['item']
        
    # df = pd.DataFrame(json_data)

    # print(df)
    # print(df.describe())
    # print(df.columns)

    for j in station_ids:
        for i in range(1):
            try:
                params ={'serviceKey' : skey, 'pageNo' : str(i+1), 'numOfRows ' : '1',
                        'dataType' : 'JSON', 'dataCd' : 'ASOS', 'dateCd' : 'HR', 'startDt' : today,
                        'startHh' : endHh, 'endDt' : today, 'endHh' : endHh, 'stnIds' : str(j) }
                # print(params)
                
                # if curr_request == max_request:
                #     print('[INFO] Max request reached')
                #     break

                response = requests.get(url, params=params, verify=False)
                print(response.content)
                json_data += json.loads(response.content)['response']['body']['items']['item']
                print(json_data)
                curr_request += 1

            except:
                df = pd.DataFrame(json_data)
                break
            df = pd.DataFrame(json_data)
            print(df)
            time.sleep(1)
    vals = df[['tm','stnId','stnNm','ta','rn','ws','wd','hm','ss','icsr','dc10Tca']].values
    print('vals_data =',vals.shape, len(vals))
    for k in range(len(vals)):
        vals[k][2] = locations[k]
        # vals[k][0] = vals[k][0].strftime('%Y-%m-%d %H:00:00')
        for j in range(len(vals[0])):

            if vals[k][j] == '':
                vals[k][j] = 0

    for i in range(len(vals)):
        print(tuple(vals[i]))
        post_data_kma(tuple(vals[i]))

if __name__ == '__main__':
    dateEnd = '2021-12-31'
    dateStart = '2023-02-15'

    dateNow = dateStart
    dt_dateStart = datetime.strptime(dateStart, '%Y-%m-%d')

    # update_KMA(1,dateStart)

    while dateNow != dateEnd:

        str_date = dt_dateStart.strftime('%Y-%m-%d')
        for i in range(0,24):
            try:
                print(i, str_date)
                update_KMA(i,str_date)
            except Exception as e:
                print(e)
                print('[INFO] Error occured')

        dt_dateStart = dt_dateStart - timedelta(1)
        dateNow = dt_dateStart.strftime('%Y-%m-%d')
        time.sleep(2)


    # print(dt_dateStart, dsdt_1)
    # update_KMA(7)