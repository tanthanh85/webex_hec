from flask import Flask, request, jsonify
from qos_config import *
from get_meeting_participant import *


current=0
update=False

app = Flask(__name__)

@app.route('/alerts', methods=['POST'])
def receive_alert():
    try:
        data = request.json
        #print(data)
        if not data:
            return jsonify({"error": "Invalid data"}), 400
        
        latency=data['result']['AverageLatency']
        # Process the received data (e.g., print it, store it, etc.)
        print(f"Latency to Webex: {data['result']['AverageLatency']}ms")
        totalParticipant=get_total_participants()
        if totalParticipant!=current:
            current=totalParticipant
            update=True
        
        search_name="avgReceive"
        #print(search_name)
        rx_bw=fetch_saved_search_results(saved_search_name=search_name)
        print(f'downstream bw status: {rx_bw["avgRx"]}kbps')
        if update==True:
            print('Live participant count changes, reflecting to the QoS configuration....')
            bw=int(current)*1000
            remaining_bw=10-int(current)*1
            
            cmd = [
            f'no policy-map dynamic',   
            f'policy-map dynamic',
            f' class WEBEX',
            f'  priority {str(bw)}',
            f' class class-default',
            f'  police {remaining_bw}m',
            f'interface gi2',
            f'service-policy output  dynamic'
            ]
            update=False
            send_commands(cmd=cmd)

            
        if int(current)>0 and int(latency)>100:         
            if float(rx_bw['avgRx'])>3000:
                print(f'Bandwidth is not congested yet: {rx_bw["avgRx"]}kbps but high latency')
                bw=int(current)*1000
                remaining_bw=10-int(current)*1
                print(f"Latency to Webex is {latency}m, the number of active webex sessions is {totalParticipant}, police bandwidth to {remaining_bw}m")
                cmd = [
                f'no policy-map dynamic',   
                f'policy-map dynamic',
                f' class WEBEX',
                f'  priority {str(bw)}',
                f' class class-default',
                f'  police {remaining_bw}m',
                f'interface gi2',
                f'service-policy output  dynamic'
            ]
                send_commands(cmd=cmd)
            else:
                print('latency is high but not because of downstream congestion')       
        elif int(current)==0 and int(latency)<60:
            print('no active Webex session and latency is acceptable (<60), no need to update QoS configuration')
            cmd= [
                f'no policy-map dynamic',
                f'policy-map dynamic',
                f' class class-default',
                f'  fair-queue',
                f'interface gi2',
                f'service-policy output  dynamic'
            ]
            send_commands(cmd=cmd)
        elif int(current)==0 and int(latency)>60:
            print('has no active Webex session but latency is greater than 60ms, pre-configure the QoS for for any new meeting. Can use AI to predict the total live participants')
            cmd = [
            f'policy-map dynamic',
            f' class WEBEX',
            f'  priority 2000',
            f' class class-default',
            f'  police 8m',
            f'interface gi2',
            f'service-policy output  dynamic'
        ]
            send_commands(cmd=cmd)
        # Return a response to acknowledge receipt
        return jsonify({"message": "Alert received"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
