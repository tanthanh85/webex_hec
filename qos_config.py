from netmiko import ConnectHandler
import os
from dotenv import load_dotenv

load_dotenv()

username=os.getenv('username')
password=os.getenv('password')

device = {
        'device_type': 'cisco_ios',
        'host': '198.18.24.1',
        'username': username,
        'password': password,
        'secret': password
    }

    

def send_commands(cmd):

    #bw=int(totalparticipant)*1000

    qos_commands = cmd
    try:
        net_connect = ConnectHandler(**device)
        net_connect.enable()
        # Send configuration commands
        output = net_connect.send_config_set(qos_commands)
        print(output)

        # Disconnect from device
        net_connect.disconnect()
    except Exception as e:
        print(f"Error configuring QoS: {str(e)}")


# if __name__=='__main__':
#     total=get_total_participants()
    
#     if int(total)>=1:
#         send_commands(totalparticipant=total)
    