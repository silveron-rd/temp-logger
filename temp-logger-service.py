import os
import glob
import sched
import time
import gammu
from datetime import datetime
 
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
ctr = 0

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
        return '%s, %s' % (temp_c, temp_f)

def main():
    service = sched.scheduler(time.time, time.sleep) 
       
    def record_temp():
        global ctr
        try:
            with open("/tmp/tempstats.log", "a") as stats_file:
                data = '\n%s, %s' % (datetime.now(), read_temp())
                stats_file.write(data)
                stats_file.close()
                if ( ctr == 11 or ctr == 0):
                    ctr = 0
                    send_sms(data)
                ctr += 1
        finally:
            service.enter(600, 1, record_temp, ())

    record_temp()
    try:
        service.run()
    except KeyboardInterrupt:
        print ('Manual break')
        return 10

    return 0

if __name__ == "__main__":
    exit(main())
