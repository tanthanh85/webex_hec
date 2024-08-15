import requests
import urllib3
urllib3.disable_warnings()
from pprint import pprint
import json
import time
from requests import ConnectionError
import os
from dotenv import load_dotenv
from json.decoder import JSONDecodeError

load_dotenv()

webex_token=os.getenv('webex_token')
webex_checksum=os.getenv('webex_checksum')
splunk_token=os.getenv('webex_splunk_token')


def get_live_meeting():
    try:
        url='https://wapmats.webex.com/pcs/api/v3/liveMeetingKPI?checksum='+webex_checksum
        headers = {"Authorization": "Bearer "+webex_token,
        "Content-Type":"application/json"}
        payload = {"siteIds":[]}
        response = requests.post(url=url,headers=headers,json=payload)
        response.raise_for_status()
        data=response.json()
        if response.status_code==200:
            if data['liveMeetingCount'] > 0:
                new_payload={"siteIds":[],"kpiResponseId":data['kpiResponseId']}
                new_url='https://wapmats.webex.com/pcs/api/v3/liveKPIForTopBadIps?checksum='+webex_checksum
                response = requests.post(url=new_url,headers=headers,json=new_payload,timeout=5)
                response.raise_for_status()
                return response.json()
            else:
                return {}
    except ConnectionError as e:
        print(e)
        return "Connection_Error"
    except JSONDecodeError as e:
        print(e)
        return "JSON_Error"
    except requests.exceptions.Timeout:
        return "Timeout"
    except requests.exceptions.HTTPError as e:
        print(e)
        print("HTTP error")
        return "HTTP_Error"
def send_to_splunk(data):
    url='https://127.0.0.1:8088/services/collector/event'
    headers = {"Authorization": "Splunk "+splunk_token,
    "Content-Type":"application/json"}
    print(data)
    for participant in data:
        try:
            response=requests.post(url=url,headers=headers,data=json.dumps({"event": participant}),verify=False,timeout=5)
            response.raise_for_status()
        except requests.exceptions.Timeout as e:
            print(e)
            print("Connection timeout to Splunk")

if __name__=='__main__':
    while True:
        data=get_live_meeting()
        if data:
            if data!="Connection_Error" or data!="JSON_Error" or data!="Timeout" or data!="HTTP_Error":
                send_to_splunk(data)
            else:
                print('Connection error to Webex, will retry in 20 seconds')
                time.sleep(20)
        else:
            print('nothing to send to Splunk')
        time.sleep(20)
    
    
    