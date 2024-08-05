from flask import Flask, request, jsonify
from qos_config import *
from get_meeting_participant import *




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

        
        search_name="avgReceive"
        #print(search_name)
        rx_bw=fetch_saved_search_results(saved_search_name=search_name)
        print(f'downstream bw status: {rx_bw["avgRx"]}kbps')
        if int(totalParticipant)>0 and int(latency)>100:
            if int(rx_bw)>9000:
                print(f'Bandwidth is congested: {rx_bw}kbps')
                bw=int(totalParticipant)*1000
                remaining_bw=10-int(totalParticipant)*1
                print(f"Latency to Webex is {latency}m, number of active webex sessions is {totalParticipant}, police bandwidth to {remaining_bw}m")
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
        elif int(totalParticipant)==0 and int(latency)<60:
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
        elif int(totalParticipant)==0 and int(latency)>60:
            print('has no active Webex session but latency is greater than 60ms, pre-configure the QoS for for any new meeting')
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
