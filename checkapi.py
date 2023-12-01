import json
import requests

API_URL = 'http://192.168.0.55'  #ENS SERVER API
PORT = ['5005','5006'] #5005 for 10 AM prediction #5006 for 4 PM Prediction
METHOD_NAME = ['BiLSTM','BiLSTM_MultiDense','BiLSTM_SingleDense','Conv_LSTM','LSTM','RNN']

for port in PORT:
    print(f"\nAPI_URL => {API_URL}:{port}")

    for method in (METHOD_NAME):

        url = f"{API_URL}:{port}/data/api/powerpred"
        headers = {"content-type": "application/json"}

        data = {
            "date": "20230801", #You can adjust the date parameter like 20231116
            "sitecode": "12345",
            "model": f'{method}'
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))

        # If you want to print the response
        print(f"\n Model : {method}\n API DATA : \n",response.json())