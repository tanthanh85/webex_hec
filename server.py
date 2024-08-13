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
        remaining_bw=10000-float(rx_bw["avgRx"])
        data_bw=10-int(totalParticipant)*1-3
        webex_bw=int(totalParticipant)*1000
        print(f'downstream used bandwidth: {rx_bw["avgRx"]}kbps')
        print(f'required bandwidth for Webex: {str(webex_bw)}kbps')
        print(f'available bandwidth: {remaining_bw}kbps')
     
        if int(totalParticipant)>0:     
            if int(latency)>100 or remaining_bw<float(webex_bw):                             
                print(f"Latency to Webex is high or remaining bandwidth is not enough for the number of active webex sessions {totalParticipant}, police data bandwidth to {data_bw}m")
                cmd = [
                f'no policy-map dynamic',   
                f'policy-map dynamic',
                f' class WEBEX',
                f'  priority {str(webex_bw)}',
                f' class class-default',
                f'  police {data_bw}m',
                f'interface gi2',
                f'service-policy output  dynamic'
                ]
                send_commands(cmd=cmd)
                     
        elif int(totalParticipant)==0 and int(latency)<80:
            print('no active Webex session and latency is acceptable (<80), no need to update QoS configuration')
            cmd= [
                f'no policy-map dynamic',
                f'policy-map dynamic',
                f' class class-default',
                f'  fair-queue',
                f'interface gi2',
                f'service-policy output  dynamic'
            ]
            send_commands(cmd=cmd)
        elif int(totalParticipant)==0 and int(latency)>=80:
            print('has no active Webex session but latency is greater than 80ms, please consider to use AI to estimate the no of webex sessions')
        #     cmd = [
        #     f'policy-map dynamic',
        #     f' class WEBEX',
        #     f'  priority 2000',
        #     f' class class-default',
        #     f'  police 8m',
        #     f'interface gi2',
        #     f'service-policy output  dynamic'
        # ]
        #     send_commands(cmd=cmd)
        # Return a response to acknowledge receipt
        return jsonify({"message": "Alert received"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/meeting', methods=['POST'])
def meeting():
    try:
        data = request.json
        #print(data)
        if not data:
            return jsonify({"error": "Invalid data"}), 400
        totalParticipant=data['result']['TotalParticipant']
        #print(totalparticipant)
        print(f'There is {totalParticipant} live Webex participant in the office, applying QoS now')

        search_name="avgReceive"
        #print(search_name)
        rx_bw=fetch_saved_search_results(saved_search_name=search_name)
        remaining_bw=10000-float(rx_bw["avgRx"])
        data_bw=10-int(totalParticipant)*1-3
        webex_bw=int(totalParticipant)*1000
        print(f'downstream used bandwidth: {rx_bw["avgRx"]}kbps')
        print(f'required bandwidth for Webex: {str(webex_bw)}kbps')
        print(f'available bandwidth: {remaining_bw}kbps')

        cmd = [
                f'no policy-map dynamic',   
                f'policy-map dynamic',
                f' class WEBEX',
                f'  priority {str(webex_bw)}',
                f' class class-default',
                f'  police {data_bw}m',
                f'interface gi2',
                f'service-policy output  dynamic'
                ]
        send_commands(cmd=cmd)


        return jsonify({"message": "Alert received"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
