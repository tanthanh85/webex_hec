from flask import Flask, request, jsonify
from qos_config import *
from get_meeting_participant import *

app = Flask(__name__)

@app.route('/alerts', methods=['POST'])
def receive_alert():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Invalid data"}), 400
        
        latency=data['result']['AverageLatency']
        # Process the received data (e.g., print it, store it, etc.)
        print(f"Latency exceeded: {data['result']['AverageLatency']}ms")
        totalParticipant=get_total_participants()
        if int(totalParticipant)>0 and int(latency)>100:
            bw=int(totalParticipant)*1000
            cmd = [
            f'policy-map dynamic',
            f' class WEBEX',
            f'  priority {str(bw)}',
            f' class class-default',
            f'  fair-queue',
            f'interface gi2',
            f'service-policy output  dynamic'
        ]
            send_commands(cmd=cmd)
        elif int(totalParticipant)>0 and (int(latency)<10):
            print('has active Webex sessions but latency is good, no need to update QoS configuration')
            cmd= [
                f'no policy-map dynamic',
                f'policy-map dynamic',
                f' class class-default',
                f'  fair-queue',
                f'interface gi2',
                f'service-policy output  dynamic'
            ]
            send_commands(cmd=cmd)
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
            print('no active Webex session but latency is greater than 60ms, pre-configure the QoS for for any new meeting')
            cmd = [
            f'policy-map dynamic',
            f' class WEBEX',
            f'  priority 1000',
            f' class class-default',
            f'  fair-queue',
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
