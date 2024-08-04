import requests

import urllib3
urllib3.disable_warnings()

splunk_instance = "https://127.0.0.1:8089"
username = "admin"
password = "C1sco12345"
public_ip="173.39.116.4/30"

def fetch_saved_search_results(saved_search_name):
    search_url = f'{splunk_instance}/servicesNS/admin/search/saved/searches/{saved_search_name}/dispatch'
    response = requests.post(search_url, auth=(username, password), verify=False)
    sid = response.json()['sid']

    results_url = f'{splunk_instance}/services/search/jobs/{sid}/results?output_mode=json'
    response = requests.get(results_url, auth=(username, password), verify=False)
    return response.json()


if __name__=='__main__':
    search_name="avgReceive"
    print(fetch_saved_search_results(saved_search_name=search_name))