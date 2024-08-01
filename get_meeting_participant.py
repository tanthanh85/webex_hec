import requests

splunk_instance = "https://127.0.0.1:8089"
username = "admin"
password = "C1sco12345"
public_ip="173.39.116.4/30"

def get_total_participants():
    # Search query to get the totalparticipantcount from the last 3 minutes
    search_query = f'search index=Webex ip={public_ip} earliest=-3m | head 1 | stats latest(totalparticipantcount) as TotalParticipant'

    # Prepare the Splunk API request
    url = f"{splunk_instance}/services/search/jobs"
    data = {
        "search": search_query,
        "output_mode": "json"
    }
    headers = {"Content-Type":"application/json","Accept":"application/json"}

    # Make the request to Splunk
    response = requests.post(url, auth=(username, password), data=data, verify=False)

    # Check if the request was successful
    if response.status_code == 201:
        job_id = response.json()["sid"]
        # print(job_id)
        results_url = f"{splunk_instance}/services/search/jobs/{job_id}/results?output_mode=json"

        # Wait for the search job to complete
        import time
        time.sleep(5)  # Adjust sleep time as necessary

        # Get the results of the search
        results_response = requests.get(results_url, auth=(username, password), verify=False)

        print(results_response.text)
        if results_response.status_code == 200:
            results = results_response.json()["results"]
            if results:
                total_participant_count = results[0].get("TotalParticipant", "N/A")
                print(f"Total Participant Count: {total_participant_count}")
                return total_participant_count
            else:
                print("No results found.")
                return 0
        else:
            print(f"Failed to get search results: {results_response.status_code}")
            return 0
    else:
        print(f"Failed to create search job: {response.status_code}")
        return 0


if __name__=='__main__':
    print(get_total_participants())