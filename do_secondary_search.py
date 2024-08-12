import requests

import urllib3
urllib3.disable_warnings()

import os
from dotenv import load_dotenv

load_dotenv()

username=os.getenv('username')
password=os.getenv('password')

splunk_instance = "https://127.0.0.1:8089"



def fetch_saved_search_results(saved_search_name):
    search_url = f'{splunk_instance}/servicesNS/admin/search/saved/searches/{saved_search_name}/dispatch?output_mode=json'
    response = requests.post(search_url, auth=(username, password), verify=False)
    
    if response.status_code==201:
        sid = response.json()['sid']
    #   print(sid)
        import time
        time.sleep(5)
        results_url = f'{splunk_instance}/services/search/jobs/{sid}/results?output_mode=json'
        response = requests.get(results_url, auth=(username, password), verify=False)
        return response.json()['results'][0]
    


if __name__=='__main__':
    search_name="avgReceive"
    print(fetch_saved_search_results(saved_search_name=search_name))