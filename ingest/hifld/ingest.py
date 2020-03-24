import csv
import os

import requests

API_KEY = os.getenv("API_KEY")

def process_int(s):
    if s == '-999':
        return None
    elif s == None:
        return None
    try:
        return int(s)
    except:
        return None

def clean_empties(d):
    for k, v in list(d.items()):
        if v == None or v == '':
            del d[k]
        elif isinstance(v, list):
            for x in v:
                if isinstance(x, dict):
                    clean_empties(x)
        elif isinstance(v, dict):
            d[k] = clean_empties(v)
    return d

with open('hifld_hospitals.csv') as fd:
    rd = csv.DictReader(fd)
    for line in rd:
        item = {
            "time": line['VAL_DATE'],
            "location": {
                "latitude": float(line['LATITUDE']),
                "longitude": float(line["LONGITUDE"])
            },
            "data": {
                "observableType": "facility",
                "type_id": f"hospital_{line['ID']}",
                "commonName": line['NAME'],
                "description": "",
                "metadata": {
                    "type": line.get("TYPE", None),
                    "status": line.get("STATUS", None),
                    "owner": line.get("OWNER", None),
                    "num_staff": process_int(line.get("TTL_STAFF", None)),
                    "num_beds": process_int(line.get("BEDS", None)),
                    "has_trauma": line.get("TRAUMA", None),
                    "has_helipad": line.get("HELIPAD", None),
                    "url": line.get("WEBSITE", None)
                }
            }
        }
        
        observation = {
            "observer": {
                "userId": "system",
            },
            "method": {
                "mode": "camera",
                "identity": "3rdparty",
                "encoding": "human"
            },
            "items": [item]
        }
        observation = clean_empties(observation)
        
        name = item['data']['commonName']
        print(f"{item['data']['type_id']} {name}")
        # print(item)
        
        obs_resp = requests.post(
            'https://totality.str8d8a.info/dev/observations',
            headers={
                'x-api-key': API_KEY,
                'Content-Type': 'application/json'
            },
            json=observation)
        
        if obs_resp.status_code != 200:
            print(f'POST observation responded with status code {obs_resp.status_code}')
            print(obs_resp.text)

        # break