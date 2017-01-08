import os
import glob
import sched
import time
from datetime import datetime
 
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

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
        try:
            with open("/tmp/tempstats.log", "a") as stats_file:
                stats_file.write('\n%s, %s' % (datetime.now(), read_temp()))
                stats_file.close()
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
