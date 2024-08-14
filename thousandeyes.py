import requests
from pprint import pprint
import urllib3
urllib3.disable_warnings()
import time
import json
from requests import ConnectionError
import os
from json.decoder import JSONDecodeError
from dotenv import load_dotenv

load_dotenv()

thousandeyes_token=os.getenv('thousandeyes_token')
splunk_token=os.getenv('thousandeyes_splunk_token')
testId= "296995"

headers = {
  'Authorization': f'Bearer {thousandeyes_token}'
}

def get_latency_to_webex():
    payload={}
    try:  
        url=f'https://api.thousandeyes.com/v7/endpoint/test-results/scheduled-tests/{testId}/network/filter'
        response=requests.post(url=url,headers=headers,json=payload,timeout=6)
        response.raise_for_status()
        data=response.json()['results'][0]
        data['destination']='Webex'
        if response.status_code==200:
            return data
        else:
            return {}
    except ConnectionError as e:
        #print(e)
        return "Connection_Error"
    
    except JSONDecodeError as e:
        #print(e)
        return "JSON_Error"

    except requests.exceptions.Timeout:
        return "Timeout"
    
def send_to_splunk(data):  
    url='https://127.0.0.1:8088/services/collector/event'
    headers = {"Authorization": "Splunk "+splunk_token,
    "Content-Type":"application/json"}
    print(data)
    print("\n\n\n")
    try:
        response=requests.post(url=url,headers=headers,data=json.dumps({"event": data}),verify=False, timeout=5)
        response.raise_for_status()
    except requests.exceptions.Timeout as e:
        print(e)
        print("Connection timeout to Splunk")


if __name__=='__main__':
    while True:
        data=get_latency_to_webex()
        if data:
            if data!="Connection_Error" or data!="JSON_Error" or data!="Timeout":
                send_to_splunk(data)
            else:
                time.sleep(3)
        else:
            print('nothing to send to Splunk')
        time.sleep(60)



