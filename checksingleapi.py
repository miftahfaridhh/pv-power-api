import json
import requests

url = f"http://192.168.0.55:5000/data/api/powerpred"
headers = {"content-type": "application/json"}

data = {
    "date": "20231001",
    "sitecode": "717800009",
    "model": "BiLSTM_MultiDense",
    "modeltime": "16"
}

response = requests.post(url, headers=headers, data=json.dumps(data))

# If you want to print the response
print(response.json())