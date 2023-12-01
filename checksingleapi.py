import json
import requests

url = f"http://192.168.0.55:5005/data/api/powerpred"
headers = {"content-type": "application/json"}

data = {
    "date": "20230801", #You can adjust the date parameter like 20231116
    "sitecode": "12345",
    "model": "BiLSTM"
}

response = requests.post(url, headers=headers, data=json.dumps(data))

# If you want to print the response
print(response.json())