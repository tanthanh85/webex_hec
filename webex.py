import requests
import urllib3
urllib3.disable_warnings()
from pprint import pprint
import json
import time
from requests import ConnectionError

webex_token='ODMzNzg1MmMtNDgyMy00NjU3LTg1MzMtMjhlNTRjYmU4NTRmYWUwZWUyOWYtNjAy_P0A1_eaec46d2-6287-43ac-bac0-1c9058b316db'
webex_checksum='v2_94f9e6a6473d4727b4e9bec3632a31a6'
splunk_token='480af2b5-20e9-4c02-bcc1-7af5da2107bf'


def get_live_meeting():
    try:
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
    except ConnectionError as e:
        print(e)
        return "Connection_Error"

def send_to_splunk(data):
    url='https://127.0.0.1:8088/services/collector/event'
    headers = {"Authorization": "Splunk "+splunk_token,
    "Content-Type":"application/json"}
    print(data)
    for participant in data:
        requests.post(url=url,headers=headers,data=json.dumps({"event": participant}),verify=False)
        

if __name__=='__main__':
    while True:
        data=get_live_meeting()
        if data:
            if data!="Connection_Error":
                send_to_splunk(data)
            else:
                print('Connection error to Webex, will retry in 15 seconds')
                time.sleep(15)
        else:
            print('nothing to send to Splunk')
        time.sleep(15)
    
    
    