import requests
from pprint import pprint
import urllib3
urllib3.disable_warnings()
import time
import json

headers = {
  'Authorization': ''
}
testId= "296995"
splunk_token=''

def get_latency_to_webex():
    payload={}  
    url=f'https://api.thousandeyes.com/v7/endpoint/test-results/scheduled-tests/{testId}/network/filter'
    response=requests.post(url=url,headers=headers,json=payload)
    data=response.json()['results'][0]
    data['destination']='Webex'
    if response.status_code==200:
        return data
    else:
        return {}
    

def send_to_splunk(data):  
    url='https://192.168.50.18:8088/services/collector/event'
    headers = {"Authorization": "Splunk "+splunk_token,
    "Content-Type":"application/json"}
    print(data)
    
    requests.post(url=url,headers=headers,data=json.dumps({"event": data}),verify=False)
        

if __name__=='__main__':
    while True:
        data=get_latency_to_webex()
        if data:
            send_to_splunk(data)
        else:
            print('nothing to send to Splunk')
        time.sleep(60)



