import os
import gammu
import glob
import logging
import sched
import time
from datetime import datetime
 
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
sensor_name = "DINING ROOM"

def send_sms(text):
    try:
        gammu_sm = gammu.StateMachine()
        gammu_sm.ReadConfig()
        gammu_sm.Init()

        message = {
            'Text': ('%s' % text),
            'SMSC': {'Location': 1},
            'Number': '9042633880'
        }
    
        gammu_sm.SendSMS(message)
    except gammu.ERR_TIMEOUT:
        pass
    except gammu.ERR_UNKNOWNRESPONSE:
        pass

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return 'temperature recorded in %s is %s C (%s F)' % (sensor_name, temp_c, temp_f)

def main():
    try:
        with open("/tmp/tempstats.log", "a") as stats_file:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data = '\n At %s, %s' % (timestamp, read_temp())
            stats_file.write(data)
            stats_file.close()
            send_sms(data)
    finally:
        logging.info('Recorded temperature')

if __name__ == "__main__":
    exit(main())
