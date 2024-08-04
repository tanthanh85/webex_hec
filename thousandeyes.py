import requests
from pprint import pprint
import urllib3
urllib3.disable_warnings()
import time
import json
from requests import ConnectionError

thousandeyes_token='1f82e605-518c-4d6e-8865-fc40ab903318'
testId= "296995"
splunk_token='8626afc9-5d78-4d21-ab0e-d8020ba1e91b'
headers = {
  'Authorization': f'Bearer {thousandeyes_token}'
}




def get_latency_to_webex():
    payload={}
    try:  
        url=f'https://api.thousandeyes.com/v7/endpoint/test-results/scheduled-tests/{testId}/network/filter'
        response=requests.post(url=url,headers=headers,json=payload)
        data=response.json()['results'][0]
        data['destination']='Webex'
        if response.status_code==200:
            return data
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
    
    requests.post(url=url,headers=headers,data=json.dumps({"event": data}),verify=False)
        

if __name__=='__main__':
    while True:
        data=get_latency_to_webex()
        if data:
            if data!="Connection_Error":
                send_to_splunk(data)
            else:
                time.sleep(15)
        else:
            print('nothing to send to Splunk')
        time.sleep(30)



