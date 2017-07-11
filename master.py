# Make Python modules available.
import os
import json
import time
from time import localtime, strftime

# Enable the required Python libraries for working with Cloudant.
from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey

import copy, random

# URL library for Internet connection
import urllib2 
from tinydb import TinyDB, Query


import serial, glob
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


jsonMask = {
    "rightNow":" ",
    "welcome": "Hello, guest!",
    "name": "MEMSiTech Application",
    "_id": "0",
    "idCount": 0,
    "type": "json"
}




#---------------------------------------------------------------------------

##-------------------------------------------
#
#   use account in Cloudant.com
#   username: 96b08c73-c2e2-4d02-a637-6006b00f0eb5-bluemix
#   password: a48cec1e622bb0dedc3b07c5443c2176c4e9f3ac2fcde2102fb3749132140173
#   
#   You should create account in console.ng.bluemix.com, add a credit card and create inginite Cloudant's account.
#
##-------------------------------------------


VCAP_SERVICES={
    "cloudantNoSQLDB": [
        {
            "credentials": {
                    "username": "96b08c73-c2e2-4d02-a637-6006b00f0eb5-bluemix",
                    "password": "a48cec1e622bb0dedc3b07c5443c2176c4e9f3ac2fcde2102fb3749132140173",
                    "host": "96b08c73-c2e2-4d02-a637-6006b00f0eb5-bluemix.cloudant.com",
                    "port": 443,
                    "url": "https://96b08c73-c2e2-4d02-a637-6006b00f0eb5-bluemix:a48cec1e622bb0dedc3b07c5443c2176c4e9f3ac2fcde2102fb3749132140173@96b08c73-c2e2-4d02-a637-6006b00f0eb5-bluemix.cloudant.com"
            },
            "syslog_drain_url": 0,
            "label": "cloudantNoSQLDB",
            "provider": 0,
            "plan": "Lite",
            "name": "iot-nongnghiep-NoSQL DB",
            "tags": [
                "data_management",
                "ibm_created",
                "lite",
                "ibm_dedicated_public"
            ]
        }
    ]
}

vcap_servicesData = VCAP_SERVICES
cloudantNoSQLDBData = vcap_servicesData['cloudantNoSQLDB']
credentials = cloudantNoSQLDBData[0]
credentialsData = credentials['credentials']
serviceUsername = credentialsData['username']
servicePassword = credentialsData['password']
serviceURL = credentialsData['url']

db = Cloudant(serviceUsername, servicePassword, url=serviceURL,timeout=1)

# import RPi.GPIO as GPIO
# import pprint
# import os, json

def InternetIsConnect():
    try:
        urllib2.urlopen('http://www.google.com/', timeout=1)
        print "Internet Connected"
        return True
    except urllib2.URLError as err:
        print "Internet Disconnected"
        return False

#
# find and return the maximun name in local Database
#
def search_localDatabase(pathDatabase):
    listdir = os.listdir(pathDatabase)
    length = len(listdir)
    dr = []
    for i in xrange(0,length):
        listdir[i] = listdir[i].replace('s_','').replace('.json','')
        try:
            int(listdir[i])
        except:
            length-=1
    numberOfJson = length
    x = 1
    nameSeason = "s_"+str(x)+".json"
    path = pathDatabase + nameSeason
    if not os.path.exists(path):
        fo = open(path,"wb")
        fo.close()        

    while (os.path.exists(path) or x <= numberOfJson):
        x+=1
        nameSeason = "s_"+str(x)+".json"
        path = str(pathDatabase) + str(nameSeason)

    nameSeason = "s_"+str(x-1)+".json"
    path = pathDatabase + nameSeason

    nameSeason = nameSeason.replace('.json',"")
    return [nameSeason,path]


def saveFileJSON(jsondata):
    try:
        tinydb.insert(jsondata)
        return True
    except:
        return False


def check_currentSeason(design_seasons):
    #####----------------#####
    #   get current Season to send data 
    #   the current Season is the max 
    #####----------------#####
    #db.connect()    # the command use 1.8s
    #Here is application place

    doc = db[design_seasons].get_design_document('design_seasons')
    arraySeasons = copy.deepcopy(doc['seasons'])
    
    jsonstr = {}
    if len(arraySeasons) > 0 :
        jsonstr = arraySeasons[len(arraySeasons)-1]
        return jsonstr['nameSeason']
    return False
    #db.disconnect()    # the command use 1.8s

def send_data_to_Cloud(nameSeason, jsondata):
    #db.connect()    # the command use 1.8s
    try:
        db[nameSeason].create_document(jsondata)
    # time.sleep(0.5)
    except: # except update 
        # time.sleep(1)
        print "error in send_data_to_Cloud"
    #db.disconnect()    # the command use 1.8s

class SYNC_local_Cloudant():
    def __init__(self):
        if namelocal in db.all_dbs():
            self._lenlocal = len(tinydb)
            self._lenCloudant = db[str(namelocal)].doc_count()- len(db[str(namelocal)].list_design_documents()) #sampledata document
        return None
    def checksize(self,namelocal):
        #Sync local database and Cloudant database (priority Big Size)
            #   Check ID in Cloud and compare ID in datalocal
            #   if ID_in_Cloud < ID_in_local, data not send when Internet was disconnected
            #   if ID_in_Cloud = 0, created new season
            #   Send document in local to Cloud to sync data
        lenlocal = self._lenlocal
        lenCloudant = self._lenCloudant
        print lenlocal, lenCloudant
        if lenlocal <= lenCloudant:
            return False
        if lenlocal > lenCloudant:
            return True

    def sync(self,namelocal):
        # in case size of local > size of Cloudant
        jsonSampleLocal = {}
        lenCloudant = self._lenCloudant
        lenlocal = self._lenlocal
        list_idCount = []

        if '_design/idCount' not in db[namelocal].list_design_documents():
            db[namelocal].create_query_index(design_document_id="_design/idCount", index_name="idCount", index_type="json", fields=[{"idCount":"asc"}])
        querylist = db[namelocal].get_query_result(selector = {'idCount':{'$gt':0}}, fields = ['idCount'],sort = [{'idCount':"asc"}],raw_result=True)
        length = len(querylist['docs'])
        for x in xrange(0,length):
            list_idCount.append(querylist['docs'][x]['idCount'])
        if lenCloudant >= 0:
            for x in xrange(1,lenlocal+1):
                if x not in list_idCount:
                    jsonSampleLocal = tinydb.search(User.idCount == x)
                    jsonSampleLocal[0]['_id'] = str(jsonSampleLocal[0]['idCount'])
                    send_data_to_Cloud(namelocal,jsonSampleLocal[0])
            return True
        return False

    def getdatabaseCloudant(self, namelocal):
    #     # in case size of local < size of Cloudant
        jsonSampleLocal = {}
        lenCloudant = self._lenCloudant
        lenlocal = self._lenlocal

        if '_design/idCount' not in db[namelocal].list_design_documents():
            db[namelocal].create_query_index(design_document_id="_design/idCount", index_name="idCount", index_type="json", fields=[{"idCount":"asc"}])
        querylist = db[namelocal].get_query_result(selector = {'idCount':{'$gt':0}}, fields = ['idCount'],sort = [{'idCount':"asc"}],raw_result=True)
        length = len(querylist['docs'])
        print querylist['docs']
        list_idCount = []
        for x in xrange(0,length):
            list_idCount.append(querylist['docs'][x]['idCount'])

def refresh_sampledata(nameSeason, jsondata):
    #####----------------#####
    #   get current Season to send data 
    #   the current Season is the max 
    #####----------------#####

    #db.connect()    # the command use 1.8s
    #Here is application place
    if len(jsondata) == 0:
        if nameSeason not in db.keys():
            return False
        return False
    
    jsondata.update(jsonMask)
    del jsondata['_id']
    del jsondata['idCount']
    del jsondata['rightNow']

    if '_design/newsampledata' not in db[nameSeason].list_design_documents():
        # Create sample data
        jsondata.update({"_id":"_design/newsampledata"})
        db[nameSeason].create_document(jsondata)
        print "Create Sample Data"
    else:
        # Update sample data
        sampleDocument = db[nameSeason]['_design/newsampledata']
        if 'idCount' in sampleDocument.keys():
            del sampleDocument['idCount']
        # docs = db[nameSeason].get_design_document("_design/newsampledata")
        nodeinCloud = sampleDocument['payload'].keys()
        for node in jsondata['payload'].keys():
            if node not in nodeinCloud:
                sampleDocument['payload'].update({node:jsondata['payload'][node]})
                sampleDocument.save()

    #db.disconnect()    # the command use 1.8s
    return True






# ----------------------------------------------------------------------------------------
#
#
#   Function for get UART CC1350
#
# ----------------------------------------------------------------------------------------


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
        return [jsonSample, True]
    else:
        print "Nothing"
        return [{}, False]


# ----------------------------------------------------------------------------------------








# Get path of the current dir, then use it to create paths:
CURRENT_DIR = os.path.dirname(__file__)

pathDatabase = os.path.join(CURRENT_DIR, 'database/')
# pathDatabase = os.path.join(CURRENT_DIR, 'temporary/')
# directory = os.path.dirname(file_path)
# os.path.exists(nameSeason)

if __name__ == '__main__':




    # -----------------------
    #
    #   Init for Serial port
    #
    # -----------------------
    try: 
        ser.open()
    except Exception as e:
        ser.close()
        ser.open()

    if ser.isOpen():
        ser.flushInput()  #flush input buffer, discarding all its contents
        ser.flushOutput() #flush output buffer, aborting current output
        while ser.inWaiting()>0:
            # time.sleep(0.5)  #give the serial port sometime to receive the data
            temp = ser.read(ser.inWaiting())
            del temp

    # ---------------------------------------------------------------------------

    db_disConnect = True
    [namelocal, path] = search_localDatabase(pathDatabase)
    print path
    try:
        tinydb = TinyDB(path)
    except IOError:
        f = open(path)
        tinydb = TinyDB(path)
    User = Query()
    while True:
        length = len(tinydb)
        jsonMask['idCount'] = length
        if ser.isOpen():
            [jsonGet, resultUART] = getUart_CC1350()
        if resultUART : # have signal UART from CC1350
            jsonMask['rightNow'] = strftime("%Y-%m-%d %H:%M:%S", localtime())
            jsonMask['idCount'] = jsonMask['idCount'] +1
            jsonGet.update(jsonMask)
            if saveFileJSON(jsonGet):
                print "Save OK"
                resetVarBuff()

        if InternetIsConnect():
            try:
                if db_disConnect:
                    db.connect()    # the command use 1.8s
                    db_disConnect = False
                if refresh_sampledata(str(namelocal),jsonGet):
                    begin = time.time()
                    SYNC_local_Cloudant()
                    if SYNC_local_Cloudant().checksize(namelocal):
                        if SYNC_local_Cloudant().sync(namelocal):
                            print "Sync Done"
                            # None
                    print "Time to sync: " + str(time.time() - begin)

                #Renew Season
                print "Have a new season ?"
                nameSeason = check_currentSeason('design_seasons')
                print nameSeason
                if not (str(namelocal) == str(nameSeason)):
                    namelocal = nameSeason
                    path = pathDatabase + namelocal + '.json'
                    try:
                        tinydb = TinyDB(path)
                    except IOError:
                        f = open(path)
                        tinydb = TinyDB(path)
                    User = Query()
                    print "yes. A new season"
                else:
                    print "No"
                time.sleep(5)
            except: 
                print 'ecapse'
        else:
            print "Raspberry Pi has to sleep in every 10s"
            db_disConnect = True
            time.sleep(60)  #Time to sleep when internet is disconnect.
    db.disconnect()    # the command use 1.8s