import serial, os, json, time
import copy, random

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
arrayName = ["pH", "Soil Humidity", "Soil Temperature", "uV", " Air Humidity", "Air Temperature"]


# jsonSensor = {
#     "name": "Temperature",
#     "value": 3
# }
jsonSample = {
    'payload':{}
}

jsonNode = {
    "name": "MST-001",
    "payload":{},
}
def check_frame(line):
    if line.find('***|') != -1: #Check START
        if line.find('|***') != -1: #Check STOP
            return True
        return False
    return False


def get_Uart():
    print ser.inWaiting()
    while ser.inWaiting()>0:
        line = ser.readline()
        line.replace('\n','()')
        print '@@@'+line+'@@@'
        if check_frame(line):
            jsontemp = copy.deepcopy(jsonNode)
            line = line.replace('***|','').replace('|***','').replace('\r\n','')
            array = line.split('|')
            nameNode = array.pop(0)
            for x in xrange(0,6):
                jsonNode['payload'].update({
                    "sensor_0"+str(x+1):{
                        'name': arrayName[x],
                        'value':float(array[x])
                        }
                    })
            jsontemp['name'] = format(int(nameNode),'02x')
            jsonSample['payload'].update({'Node_01':jsontemp})
            # print jsonSample

if __name__ == '__main__':
    # try:
    #     ser.open()
    # except Exception as e:
    #     ser.close()
    #     ser.open()
    ser.flushInput()
    ser.flushOutput()
    time.sleep(1)
    while True:
        try:
            if ser.inWaiting()>0:
                get_Uart()
        except (KeyboardInterrupt, SystemExit) as e:
            ser.flushInput()
            ser.flushOutput()
            ser.close()


            # print '---!'+line+'!---'
       # time.sleep(1)
