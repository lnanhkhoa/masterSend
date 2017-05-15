import serial,os,json,time


ser = serial.Serial('/dev/ttyACM0',115200,timeout=5)

ser.flushInput()
ser.flushOutput()

if __name__ == '__main__':
    while True:
        while ser.inWaiting()>0:
            print "a"
            #line = ser.read(ser.inWaiting())
            line = ser.readline()
            line = line.replace('\n','|')
            print '---!'+line+'!---'
       # time.sleep(1)
