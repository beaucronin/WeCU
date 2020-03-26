import os
import json
import requests

from textdistance import hamming

API_KEY = os.getenv("API_KEY")

def lookup_hospital(f):
    def best_match(m):
        hs = [hamming(f['Facility Name'].lower(), x['Data']['commonName'].lower()) for x in m]
        return hs.index(min(hs))
    
    lat_s = f['Facility Latitude']
    long_s = f['Facility Longitude']
    if not (lat_s and long_s):
        return None
    url = f"https://totality.str8d8a.info/dev/observations/facilities/hospital/{f['Facility Latitude']},{f['Facility Longitude']}"
    resp = requests.get(url).json()
    if len(resp) == 0:
        # print("enlarging")
        resp = requests.get(url, params={'precision': '5'}).json()
    
    # print(resp)
    if len(resp) == 0:
        # print(f"{f['Facility Name']:80} ==> NOT FOUND")
        return None
    else:
        # print(f"{f['Facility Name']:80} ==> {resp[best_match(resp)]['Data']['commonName']}")
        # print(f" ==== {', '.join([x['Data']['commonName'] for x in resp])}")
        return resp[best_match(resp)]

with open('nys-facilities.json') as fd:
    facilities = json.loads(fd.read())
    
with open('nys-beds.json') as fd:
    beds = json.loads(fd.read())
    
facility_columns = [c['name'] for c in facilities['meta']['view']['columns']]
data = {}
for vals in facilities['data']:
    row = dict(zip(facility_columns, vals))
    row['Beds'] = {}
    row['Services'] = []
    data[row["Facility ID"]] = row

beds_columns = [c['name'] for c in beds['meta']['view']['columns']]
for vals in beds['data']:
    row = dict(zip(beds_columns, vals))
    if row['Attribute Value'] == '0':
        continue
    if row['Attribute Type'] == 'Bed':
        data[row['Facility ID']]['Beds'][row['Attribute Value']] = (int(row['Measure Value']), row['Effective Date'])
    if row['Attribute Type'] == 'Service':
        data[row['Facility ID']]['Services'].append(row['Attribute Value'])

for f in data.values():
    if not f['Description'] == 'Hospital':
        continue

    h = lookup_hospital(f)
    if not h:
        continue

    items = []
    for b, v in f['Beds'].items():
        type_id = f"{h['TypeId']}_Beds_{b.replace(' ', '_')}"
        items.append({
            "time": v[1],
            "location": {
                "latitude": h["Location"]["Latitude"],
                "longitude": h["Location"]["Longitude"]
            },
            "data": {
                "observableType": "reservoir",
                "facility_id": h["TypeId"],
                "type_id": type_id,
                "attributes": {
                    "matterContents": "humans",
                    "site": "inhabitable",
                    "support": "on-ground",
                    "envelope": "building",
                    "shape": "structural",
                    
                },
                "capacity": {
                    "capacityPopulation": {
                        "amount": v[0],
                        "unit": "persons"
                    }
                },
                "purpose": {
                    "usages": ["personal services"]
                }
            }
        })
        
    observation = {
        "observer": {
            "userId": "system",
        },
        "method": {
            "mode": "web",
            "identity": "3rdparty",
            "encoding": "human"
        },
        "items": items
    }
    
    print(f['Facility Name'])
    print(json.dumps(observation))
    # obs_resp = requests.post(
    #     'https://totality.str8d8a.info/dev/observations',
    #     headers={
    #         'x-api-key': API_KEY,
    #         'Content-Type': 'application/json'
    #     },
    #     json=observation)
    
    # if obs_resp.status_code != 200:
    #     print(f'POST observation responded with status code {obs_resp.status_code}')
    #     print(obs_resp.text)
