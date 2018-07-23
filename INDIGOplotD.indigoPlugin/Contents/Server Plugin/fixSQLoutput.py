import sys
import os
import time
import json
import getNumber.getNumber as GT
#print "hello"

def makeEvents():
    return 


d0 = time.time()


params      = json.loads(sys.argv[1])
fileDir     = params["fileDir"]
inputFile   = params["inputFile"]
outputFile  = params["outputFile"]
logFile     = params["logFile"]
if "startID" in params:
    startID = int(params["startID"])
else:
    startID = 0

if "makeEventFile" in params:
    makeEventFile = int(params["makeEventFile"])
else:
    makeEventFile = None


limitHigh = 10000000000.
limitLow  = -1800000.

if inputFile==outputFile:
    sameFile=True
    outputFile = outputFile+"-o"
else:
    sameFile=False



#remove duplicates, ie same SQL ID    &     samedate and same value

if  not os.path.isfile(fileDir+inputFile):
    print "inputFile "+fileDir+inputFile+" does not exist"
    
    exit()
f=open(fileDir+inputFile,"r")
if sameFile:
    g=open(fileDir+outputFile,"w")
else:
    g=open(fileDir+outputFile,"a")
logF=open(logFile+".log","a")

logF.seek(0,2)
size = logF.tell()
#print " size "+str(size)


if size > 500000:
    try:
        logF.close()
        try:			# error if it does not exit
            os.remove( logFile+".1.log" )
        except:
            pass
        try:			# error if it does not exit
            os.rename( logFile+".log", logFile+".1.log")
        except:
            pass
        logF= open( logFile+".log" , "a")
    except:
        pass


logF.write("\n\n input "+inputFile)
logF.write("\n output "+outputFile+"\n")
logF.write(" starting at id: "+str(startID)+"\n")

lastID=-1
lastDate =" "
lastValue =" "
idCount=0
inCount=0
valCount=0
valCountBAD=0
valDateCount=0
dateCount =0
outCount =0
lCount=0
lastLine=""
iDate =0

for line in f.readlines():
    l=line.strip("\n").strip(" ").split(";")
    inCount+=1

## done in awk after sql statement
    if len(l) <3:
        lCount+=1
        continue

#    logF.write(str(l)+"\n")
    id = int(l[0])
    if id <=lastID:
        idCount+=1
        continue
    if id <=startID:
        idCount+=1
        continue

    if lastID >0 and  abs(id-lastID) > 500000:  # something nmust be wrong
        idCount+=1
        continue


    dateStr = l[1]
    if len(dateStr) <14:
        iDate+=1
        continue
    if dateStr.find(":") >-1:
        iDate+=1
        continue


    if line.find("data unavailable") >-1:
        lCount+=1
        continue

    
    l[2] = str(GT.getNumber(l[2]))
    if l[2] =="x":
        valCountBAD+=1
        continue
    valCount+=1

    l1 = l[1].split(".")[0]
    if lastDate == l1 and lastValue==l[2]:
        valDateCount+=1
        continue

    if lastDate != l1:
        if lastID >0:		# skip the first one
            g.write(lastLine)
            outCount+=1
    else: dateCount+=1
    lastLine =l[0]+";"+l[1]+";"+l[2]+"\n"
    lastID =id
    lastDate = l1
    lastValue = l[2]
        
if lastID >0:				# write out last record
    g.write(lastLine)
    outCount+=1

logF.write(" last  id written: "+str(lastID)+"\n")

logF.write(u"   read/written: "+str(inCount).rjust(8)+"/"+str(outCount).rjust(8)
    +"; Val OK: "+str(valCount).rjust(7)
    +"       records;   removed .. due to duplicate IDs: "+str(idCount).rjust(7)
    +"; date: "+str(iDate).rjust(7)
    +"; noValue: "+str(lCount).rjust(7)
    +"; sameDate&Value: "+str(valDateCount).rjust(7)
    +"; Val not float of T/F: "+str(valCountBAD).rjust(7)
    +"; sameSecond: "+str(dateCount).rjust(7)
    +"   elapsed time: "+str(time.time()-d0)[:6])

if sameFile:
    os.remove(fileDir+inputFile)
    os.rename(fileDir+outputFile,fileDir+inputFile)
else:
    os.remove(fileDir+inputFile)
f.close()
g.close()


logF.close()