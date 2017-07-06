#!/usr/bin/python

import serial, glob
import copy
import json
import time
from time import localtime, strftime
#initialization and open the port

#possible timeout values:
#    1. None: wait forever, block call
#    2. 0: non-blocking mode, return immediately
#    3. x, x is bigger than 0, float allowed, timeout block call

temp_list = glob.glob ('/dev/ttyACM*')

print temp_list
ser = serial.Serial()
ser.port = "/dev/ttyACM0"
# ser.port = "/dev/ttyUSB7"
#ser.port = "/dev/ttyS2"
ser.baudrate = 115200
ser.bytesize = serial.EIGHTBITS #number of bits per bytes
ser.parity = serial.PARITY_NONE #set parity check: no parity
ser.stopbits = serial.STOPBITS_ONE #number of stop bits
#ser.timeout = None          #block read
ser.timeout = 1            #non-block read
#ser.timeout = 2              #timeout block read
ser.xonxoff = False     #disable software flow control
ser.rtscts = False     #disable hardware (RTS/CTS) flow control
ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
ser.writeTimeout = 2     #timeout for write

arrayName = ["pH", "Soil Humidity", "Soil Temperature", "uV", " Air Humidity", "Air Temperature"]

addressNode = []

dataNode = []

jsonNode = {}

jsonSample = {}

jsonSensor = {}



def setVarBuff():
    global jsonNode, jsonSample, jsonSensor
    jsonNode = {
        "name": "",
        "payload":{}
    }
    jsonSample = {
        "payload": {
        }
    }
    jsonSensor = {
        "name": "",
        "value": 0
    }

def resetVarBuff():
    global jsonNode, jsonSample, jsonSensor
    addressNode = []
    dataNode = []
    jsonNode = {}
    jsonSample = {}
    jsonSensor = {}

def operator(addressNode):
    if len(addressNode)>0:
        setVarBuff()
        for i in range(0,len(addressNode)):
            jsontemp = copy.deepcopy(jsonNode)
            jsontemp['name'] = addressNode[i]
            for x in range(0,6):
                jsonTempSensor = copy.deepcopy(jsonSensor)
                jsonTempSensor['name'] = arrayName[x]
                jsonTempSensor['value'] = dataNode[i][x]
                jsontemp['payload'].update({"sensor_0"+str(x+1):jsonTempSensor})
            jsontemp.update({"rightNow": strftime("%Y-%m-%d %H:%M:%S", localtime())})
        jsonSample['payload'].update({"Node_0"+str(i+1):jsontemp})


def check_frame(line):
    if line.find("***|") != -1: # check Start
        if line.find("|***") != -1: # check stop
            return True
        return False
    return False


def getUart_CC1350():
    count = 0
    if ser.inWaiting()>0:
        time.sleep(5)   # Time to waiting buffer is done
        setVarBuff()    #set when get data, reset when send data to Cloud for the next time
        while ser.inWaiting()>0:
            line = ser.readline()
            if check_frame(line):
                start = time.time()
                line = line.replace('\r\n','').replace("***|","").replace("|***","")
                array = line.split('|')
                # print array
                nameNode = array.pop(0)
                if nameNode in addressNode:
                    dataNode[addressNode.index(nameNode)] = array
                    # print dataNode
                else:
                    addressNode.append(nameNode)
                    dataNode.append([])
                    dataNode[addressNode.index(nameNode)] = array
                count+=1
                print "Time to get Uart: " + str(time.time() - start)
            else:
                print "It's not my frame."
        if count>0:
            operator(addressNode)
        return True
    else:
        print "Nothing"
        return False



if __name__ == '__main__':

    try: 
        ser.open()
    except Exception as e:
        ser.close()
        ser.open()

    if ser.isOpen():
        ser.flushInput()  #flush input buffer, discarding all its contents
        ser.flushOutput() #flush output buffer, aborting current output
        while ser.inWaiting()>0:
            time.sleep(0.5)  #give the serial port sometime to receive the data
            temp = ser.read(ser.inWaiting())
            del temp

        while True:
            time.sleep(3) # do another thing
            if ser.isOpen():
                if getUart_CC1350():
                    print json.dumps(jsonSample,sort_keys=True, indent=4, separators=(',',':'))
                    resetVarBuff()

                else:
                    print "Nothing"
    else:
        print "cannot open serial port "