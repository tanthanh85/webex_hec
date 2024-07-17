import requests
import urllib3
urllib3.disable_warnings()
from pprint import pprint
import json
import time

webex_token=''
webex_checksum=''
splunk_token=''


def get_live_meeting():
    url='https://wapmats.webex.com/pcs/api/v3/liveMeetingKPI?checksum='+webex_checksum
    headers = {"Authorization": "Bearer "+webex_token,
    "Content-Type":"application/json"}
    payload = {"siteIds":[]}
    response = requests.post(url=url,headers=headers,json=payload)
    data=response.json()
    if response.status_code==200:
        if data['liveMeetingCount'] > 0:
            new_payload={"siteIds":[],"kpiResponseId":data['kpiResponseId']}
            new_url='https://wapmats.webex.com/pcs/api/v3/liveKPIForTopBadIps?checksum='+webex_checksum
            response = requests.post(url=new_url,headers=headers,json=new_payload)
            return response.json()
        else:
            return {}


def send_to_splunk(data):
    url='https://192.168.50.18:8088/services/collector/event'
    headers = {"Authorization": "Splunk "+splunk_token,
    "Content-Type":"application/json"}
    print(data)
    for participant in data:
        requests.post(url=url,headers=headers,data=json.dumps({"event": participant}),verify=False)
        

if __name__=='__main__':
    while True:
        data=get_live_meeting()
        if data:
            send_to_splunk(data)
        else:
            print('nothing to send to Splunk')
        time.sleep(60)
    
    
    