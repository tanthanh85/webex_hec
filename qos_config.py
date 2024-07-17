from netmiko import ConnectHandler
from get_meeting_participant import *

device = {
        'device_type': 'cisco_ios',
        'host': '192.168.50.19',
        'username': 'admin',
        'password': 'admin'
    }

def send_commands(totalparticipant):

    bw=totalparticipant*1000

    qos_commands = [
            f'policy-map dynamic',
            f' class WEBEX_TRAFFIC',
            f'  priority {bw}',
            f' class class-default',
            f'  fair-queue',
        ]
    try:
        net_connect = ConnectHandler(**device)
        # Send configuration commands
        output = net_connect.send_config_set(qos_commands)
        print(output)

        # Disconnect from device
        net_connect.disconnect()
    except Exception as e:
        print(f"Error configuring QoS: {str(e)}")


if __name__=='__main__':
    total=get_total_participants()
    
    if total>=1:
        send_commands(totalparticipant=total)
    