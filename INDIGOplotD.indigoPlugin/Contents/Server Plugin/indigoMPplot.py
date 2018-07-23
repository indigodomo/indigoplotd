#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# matplot grapher for INDIGOplot Plugin
# 2014-03-24
# Developed by Karl Wachs
# karlwachs@me.com
# please use as you see fit, no warrenty
import os, pwd, subprocess, sys
import time
import datetime
import json
import matplotlib as mlp
mlp.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.dates  import DateFormatter,WeekdayLocator, HourLocator,DayLocator, MonthLocator
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import scipy.interpolate
import copy
#import numpy as np
#import gc
import resource
#import psutil



#import simplejson as json

#
#
########################################
#	Main loop
########################################
def main():
# main loop check for comamnds and gather data and create plots
    global indigoPlotDataDir, parameterFile, indigoPNGdir
    global quitNOW , fileData, parameterFile
    global plotSizeNames, plotTimeNames, timeDataNumbers, dataVersion, parameterVersion,debugEnable,numberOfTimeTypes
    global PLOT,oldPLOT, NOTdataFromTimeSeries
    global oldfileData,newData
    global dataColumnCount,  noOfDays, numberOfMinutesInTimeBins, numberOfTimeTypes, numberOfTimeTypes, numberOfTimeBins, quitNOW, d0
    global dataOffsetInTimeDataNumbers
    dataColumnCount				=	3
    noOfDays					=	[30,100,1000]
    numberOfMinutesInTimeBins	=	[5,60,60*24]
    numberOfTimeBins			=   [int((60*24*noOfDays[0])/numberOfMinutesInTimeBins[0]),
                                    int((60*24*noOfDays[1])/numberOfMinutesInTimeBins[1]),
                                    int((60*24*noOfDays[2])/numberOfMinutesInTimeBins[2])]
                                    
    timeDataNumbers				=	[]
    resettimeDataNumbers()
    
    oldfileData = [["0","0"] for t in range(numberOfTimeTypes) ]
    newData=True
    NOTdataFromTimeSeries={}
    parameterFileTimeOld	= -1
    parameterFileTimeNew	= -1
    cmdFileTimeOld			= -1
    cmdFileTimeNew			= -1
    timeCount				= 0
    time.sleep(1)
    waitTime                = 3
    thePlotCount            = 0
    oldPLOT                 = {}
    loopCount               = 0
    while not quitNOW:
        fNamesToPlot=[""]
        time.sleep(waitTime)
        if thePlotCount > 300: break			#  reboot every 300 times to clear memory.
        
        timeCount +=1
        if timeCount > 720./waitTime: break	# nothing has changed in the last 12 minutes .. exit

        if os.path.isfile(matplotcommand):
            sendToLog("new matplot input command found",FULL=True,level=1)
            try:
                f = open (matplotcommand,"r")
                fNamesToPlot = json.loads(f.read())
                f.close()
                if isinstance(fNamesToPlot, str) or isinstance(fNamesToPlot, unicode):
                    fNamesToPlot=[fNamesToPlot]
                for fn in fNamesToPlot:
                    sendToLog("matplot input command read >>"+fn+"<<",FULL=True ,level=1)
                os.remove( matplotcommand )
            except:
                sendToLog("matplot input command file present, but empty, can't read ",FULL=True,level=0)
                try:
                    f.close()
                    os.remove( matplotcommand )
                except:
                    pass
                continue
            parameterFileTimeNew = os.path.getmtime(parameterFile)
            if parameterFileTimeOld != parameterFileTimeNew:#  or parameterFileTimeOldD != parameterFileTimeNewD:
                readPlotParameters()
                parameterFileTimeOld = parameterFileTimeNew
            getDiskData(0)
            getDiskData(1)
            getDiskData(2)
            getEventData()
            d0= datetime.datetime.now()
            plotNow(fNamesToPlot)
            thePlotCount    += 1
            timeCount        = 0
            sendToLog(secMillis(d0)+" S.m; new param.- finished +  count "+ str(thePlotCount)+",  memory used: "+str(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024.*1024.))[:6]+"[MB]" ,FULL=False, level=1)

    sendToLog("stopping program, no new data for too long, # of plots since new data: "+str(thePlotCount)+ "  # of cycles:"+str(timeCount),FULL=True,level=0)
    logHandle.close()
    # exit program
    return



########################################
def sendToLog(theText,FULL=False, level=1):
    global indigoPlotDataDir, parameterFile, indigoPNGdir
    global msgCount, logHandle
    global debugEnable

#	logHandle= open( indigoPlotDataDir+"matplot.log" , "a")

    if level ==2: return
    logHandle.seek(0,2)
    size = logHandle.tell()
    if size > 5000000:
        try:
            logHandle.close()
            try:			# error if it does not exit
                os.remove( matplotlog1 )
            except:
                pass
            try:			# error if it does not exit
                os.rename( matplotlog, matplotlog1)
            except:
                pass
            logHandle= open( matplotlog , "a")
        except:
            pass

    if FULL:
        dString = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+" PID:" + myPID
    else:
        dString=datetime.datetime.now().strftime("%M:%S.%f")[:8]

    if level ==0 :
        logHandle.write(dString+ " --------------\n")
        logHandle.write(dString+ " " + theText.encode('utf8') +"\n")
        logHandle.write(dString+ " --------------\n")
    else:
        logHandle.write(dString+ " " + theText.encode('utf8') +"\n")


    logHandle.flush()

    return




########################################
#	read / write configuration parameters from file
########################################

########################################
def readPlotParameters():
    global PLOT,oldPLOT, DEVICE, dataColumnToDevice0Prop1Index
    global indigoPlotDataDir, parameterFile,parameterFileD, indigoPNGdir
    global dataOffsetInTimeDataNumbers


    input ="--"
    if os.path.isfile(parameterFile):
        for ii in range (3):
            try:
                input= open(parameterFile , "r").read()
                xxxx=json.loads(input)
                PLOT                            = copy.deepcopy(xxxx["PLOT"])
                DEVICE                          = copy.deepcopy(xxxx["DEVICE"])
                dataColumnToDevice0Prop1Index   = copy.deepcopy(xxxx["dataColumnToDevice0Prop1Index"])
                dataOffsetInTimeDataNumbers     = copy.deepcopy(xxxx["dataOffsetInTimeDataNumbers"])
                indigoPNGdir                    = copy.deepcopy(xxxx["PNGdir"])
                sendToLog(" plot   parameters from indigoplotD first     1000 char\n " + unicode(json.dumps(PLOT,sort_keys=True, indent=2))[:100]+" ...",level=1 )
                #sendToLog(" DEVICE parameters from indigoplotD first     1000 char\n " + unicode(DEVICE.dumps(PLOT,sort_keys=True, indent=2))[:1000]+" ...",level=1 )
                xxxx=""
                input=""
                return True
            except  Exception, e:
                sendToLog("Line '%s' has error='%s'" % (sys.exc_traceback.tb_lineno, e),1)
                time.sleep(1)
        return False
    else:
        sendToLog(" no plot parameters from indigoplotD\n " ,1 )
        return False


########################################
def resettimeDataNumbers():
    global  numberOfPlots,  noOfDays, numberOfMinutesInTimeBins, numberOfTimeTypes, numberOfTimeBins, dataColumnCount, quitNOW
    global timeDataNumbers
    timeDataNumbers			=	[[0  for l in range(numberOfTimeBins[j])] for j in range(numberOfTimeTypes)]

########################################
def getEventData():
    global eventData, eventIndex, DEVICE, dataColumnToDevice0Prop1Index, eventType
    eventData  ={}
    eventIndex ={}
    eventType  ={}
    #sendToLog("dataColumnToDevice0Prop1Index " + unicode(dataColumnToDevice0Prop1Index) )
    for theCol in range(1,len(dataColumnToDevice0Prop1Index)):
            devNo= dataColumnToDevice0Prop1Index[theCol][0]
            stateNo=dataColumnToDevice0Prop1Index[theCol][1]
            resetType = "-0"
            zero      = "-zero"
            #print theCol, devNo, DEVICE[str(devNo)]["measurement"][stateNo]
            if DEVICE[str(devNo)]["measurement"][stateNo].find("event") >-1:
                if DEVICE[str(devNo)]["measurement"][stateNo].find("eventUP") >-1:
                    event="up"
                elif DEVICE[str(devNo)]["measurement"][stateNo].find("eventDOWN") >-1:   
                    event="down"
                elif DEVICE[str(devNo)]["measurement"][stateNo].find("eventCHANGE") >-1:   
                    event="change"
                elif DEVICE[str(devNo)]["measurement"][stateNo].find("eventCOUNT") >-1:   
                    event="count"
                    if DEVICE[str(devNo)]["resetType"][stateNo].find("0") ==-1:   
                        resetType = "-"+DEVICE[str(devNo)]["resetType"][stateNo]
                        if   resetType.find("day")   >-1: resetType = "-day" 
                        elif resetType.find("week")  >-1: resetType = "-week" 
                        elif resetType.find("month") >-1: resetType = "-month" 
                        elif resetType.find("year")  >-1: resetType = "-year" 
                        else:                             resetType = "-bin" 
                    if DEVICE[str(devNo)]["measurement"][stateNo].find("zero") >-1:   
                        zero = "-zero"
                else:
                    event="any"
                
                eventData[str(theCol)]  = []
                eventIndex[str(theCol)] = 0
                eventType[str(theCol)]  = event+resetType+zero
                ### try it 3 time s
                errorC =0
                for ii in range(3):
                    try:
                        #print "doing: ..."+indigoPlotDataDir+"sql/"+unicode(DEVICE[unicode(devNo)]["Id"]) + "-" + DEVICE[unicode(devNo)]["state"][stateNo]
                        f=open(indigoPlotDataDir+"sql/"+unicode(DEVICE[unicode(devNo)]["Id"]) + "-" + DEVICE[unicode(devNo)]["state"][stateNo], "r")
                        datax =[]
                        nn=0
                        for line in f.readlines():
                            dd=line.strip("\n").split(";")
                            if len(dd)==3:
                                datax.append([dd[1],1,0,0,0,0,1,float(dd[-1])]) # same format as plotDatastore
                                datax[nn][2] = datetime.datetime.strptime(dd[1],"%Y%m%d%H%M%S").weekday()
                                if nn >0:
                                    if dd[1][-8:]  ==   "01000000":  # last bin  in month
                                        datax[nn-1][3] = 1
                                    if dd[1][-10:] == "0101000000":  # last bin  in year
                                        datax[nn-1][4] = 1
                            nn+=1         #  0  1 2 3 4 5 6 7 
                        f.close()
                        #print datax
                        eventData[str(theCol)] = datax
                        eventIndex[str(theCol)]= nn
                        #print " read done", theCol, eventIndex[str(theCol)], eventData[str(theCol)][0:2]
                        errorC =0
                        break
                    except  Exception, e:
                        sendToLog("Line '%s' has error='%s'" % (sys.exc_traceback.tb_lineno, e),1)
                        sendToLog("DEVICE " + unicode(DEVICE[str(devNo)]["Id"])+";  col#:"+ str(theCol)+" no event data ?" ,level=1)
                        time.sleep(4)
                        errorC +=1
                if errorC==0: sendToLog("read event ...sql/"+unicode(DEVICE[unicode(devNo)]["Id"]) + "-" + DEVICE[unicode(devNo)]["state"][stateNo]+" ok" ,level=1)
    #print " read event done"
    #sendToLog("eventIndex " + unicode(eventIndex) ,level=1)
    #sendToLog("eventData  " + unicode(eventData)[0:200] ,level=1)
    
########################################
def getDiskData(tType):
    global fileData
    global indigoPlotDataDir, parameterFile, indigoPNGdir
    global plotSizeNames, plotTimeNames, fileData, dataVersion, parameterVersion,debugEnable
    global newData
    global oldfileData
    global dataColumnCount,  noOfDays, numberOfMinutesInTimeBins, numberOfTimeTypes, numberOfTimeTypes, numberOfTimeBins, timeDataNumbers
    
    if os.path.isfile(fileData[tType]):
        i=0
        f=open(fileData[tType], "r")
        for i, l in enumerate(f):
            pass
        f.close()
        if i+1 !=numberOfTimeBins[tType]:
            if i < 50:
                sendToLog(" read file "+fileData[tType] +" file line: "+str(i+1)+"  rejecting too small  " ,level=1)
                quitNOW =True
                return
            else:
                sendToLog(" read file "+fileData[tType] +" file line: "+str(i+1)+";  and expexted line: " + str(numberOfTimeBins[tType]),level=1)
                numberOfTimeBins[tType] =i+1
                noOfDays[tType]= ((i+1)*numberOfMinutesInTimeBins[tType])/(60*24)
                timeDataNumbers[tType]=	[0  for l in range(numberOfTimeBins[tType])]
                sendToLog("changed # of days to:  "+str(noOfDays[tType]) +" len(timeDataNumbers) is now:  " + str(len(timeDataNumbers[tType])),level=1)


        f=open(fileData[tType], "r")
        line = f.readline()
        if len(line) < 16: return  False # checking length of first 2 item. its the date string YYYYMMDD +HH + MM so 8 10 12 +";0.0" +4 = 12 14 16
        
        f.close()
        sep=";"
            
        if len(line.split(sep)[0]) < 8: return False # junk data

        dataColumnCount ==0
        f= open( fileData[tType] , "r")
        theIndex=0
        for line in f.readlines():
            test = line.strip("\n").strip(" ").strip(" "+sep).split(sep)
            if len(test[0]) < 8: return False
            if len(test) > dataColumnCount + 2 + dataOffsetInTimeDataNumbers: dataColumnCount=len(test) - 2 - dataOffsetInTimeDataNumbers

            timeDataNumbers[tType][theIndex] =test[:]
            theIndex+=1
        f.close()

        for line in range(theIndex):
            if len(timeDataNumbers[tType][line]) == dataColumnCount + 2 + dataOffsetInTimeDataNumbers:continue
            for jj in range(dataColumnCount - len(test) + 2 + dataOffsetInTimeDataNumbers):
                timeDataNumbers[tType][line].append("")
    
    # check if new data
    if oldfileData[tType] !=timeDataNumbers[tType]:
        oldfileData[tType] = copy.deepcopy(timeDataNumbers[tType])
        newData=True
    else:
        newData=False

    sendToLog(" timeDataNumbers "+str(len( timeDataNumbers[tType])) ,level=1)# +"\n"+str(timeDataNumbers[tType]) ,level=1)



    sendToLog(" reading data, tType: "+ str(tType) +"   newData:"+str(newData),level=1)

    return True






########################################
def firstLastDayToPlot(days, shift, type):


    d  =  datetime.date.today()
    dd =  datetime.datetime(d.year,d.month,d.day,0,0,0)
    ddn = datetime.datetime.now()
    earliestDay, lastDay=d,d

    if days ==0: return earliestDay, lastDay
    
    if type ==2  or type ==1 :  ###  for day & hour plot
        if  shift >=0:
            earliestDay		= ( dd +datetime.timedelta(1) - datetime.timedelta( days+ shift) )
            lastDay			= ( dd +datetime.timedelta(1) - datetime.timedelta( shift ) )
            return earliestDay, lastDay

    if type ==0  :  ###  for minute plot
        if shift>=0:
            YRIGHT 			= dd+datetime.timedelta(1)
            lastDay			= ( YRIGHT - datetime.timedelta( shift)                                       )
            earliestDay		= ( YRIGHT - datetime.timedelta( days+ shift ) )
            return earliestDay, lastDay
            
        elif shift ==-1: # this is for continous shift every hour
            x = datetime.datetime.now()
            YRIGHT0			=	ddn -datetime.timedelta(minutes=x.minute,seconds=x.second)
            YRIGHT			=	YRIGHT0 + datetime.timedelta( hours=1)
            lastDay			= ( YRIGHT                                       )
            earliestDay		= ( YRIGHT0 - datetime.timedelta( days ))
            return earliestDay, lastDay


    curMonth	 = d.month
    curWeekday 	 = d.weekday()
    curDayOfMonth= d.day
    curYear		 = d.year
    if   curMonth < 4:  firstMonth=1
    elif curMonth < 7:  firstMonth=4
    elif curMonth < 10: firstMonth=7
    else:				firstMonth=10

    if   shift ==-10: # this is for one fixed week monday - sunday
        earliestDay 	= (dd - datetime.timedelta( curWeekday ) )
        lastDay 		= (dd + datetime.timedelta( 7-curWeekday ) )

    elif shift ==-11: # this is for TWO fixed week monday - sunday
        earliestDay 	= (dd - datetime.timedelta( 7+curWeekday ) )
        lastDay			= (dd + datetime.timedelta( 7-curWeekday ) )

    elif shift ==-20: # this is for one fixed month
        earliestDay 	= datetime.datetime(curYear, curMonth, 1)
        if curMonth <12:
            lastDay 	= datetime.datetime(curYear, curMonth+1, 1)
        else:
            lastDay 	= datetime.datetime(curYear+1, 1, 1)

    elif shift ==-30: # this is for one Fixed Quarter
        earliestDay 	= datetime.datetime(curYear, firstMonth, 1)
        if firstMonth < 10:
            lastDay 	= datetime.datetime(curYear, firstMonth+3, 1)
        else:
            lastDay 	= datetime.datetime(curYear+1, 1, 1)

    elif shift ==-40: # this is for one Fixed Year
        earliestDay 	= datetime.datetime(curYear, 1, 1)
        lastDay 		= datetime.datetime(curYear+1, 1, 1)


    return earliestDay, lastDay


########################################
def secMillis(d0):
    d =datetime.datetime.now()-d0
    return (str(d.seconds).rjust(2)+"."+str(d.microseconds))[:5]


########################################
def plotNow(filenamesToPlot):
    global PLOT,oldPLOT, NOTdataFromTimeSeries
    global newData, plotDatastore
    global numberOfPlots,  noOfDays, numberOfMinutesInTimeBins, numberOfTimeTypes, numberOfTimeBins, dataColumnCount
    global indigoPlotDataDir, parameterFile, indigoPNGdir,indigoPath
    global myPID, msgCount, logHandle, quitNOW
    global plotSizeNames, plotTimeNames, timeDataNumbers, dataVersion, parameterVersion,debugEnable
    global xtimeCol, columnDataToPlot,  countTimeBinsMax, countTimeBinsWithDataMax, zeroYColumn
    global yMinL, yMinR, yMaxR, yMaxL, xMax, xMin, y1, y2, firstDaytoPlot, lastDaytoPlot, lastBinTime, colsToPlot, colsToPlotB,columnsToPlot, numberofNonTimeBins 
    global noOfMinutesInTimeBins, emptyBlanks, MHD, d0, d1, doPLOT, zeroYValue,  BordOff, Xfline1, Xfline2, xTime, DeviceNamePlotpng0
    global eventData, eventIndex, DEVICE, dataColumnToDevice0Prop1Index
    
    emptyBlanks		= [" " for i in range(100)]
    MHD				= ["Minute","Hour","Day"]
    d0= datetime.datetime.now()
    d1 = datetime.datetime.now()- datetime.timedelta(hours=d0.hour,minutes=d0.minute,seconds=d0.second,microseconds=d0.microsecond)# set to midnight today  =  hours, minutes, seconds to 0
    d1= d1+datetime.timedelta(days=1)
    sendToLog("Starting New PLOTS",FULL=True,level=1 )
    for nPlot in PLOT:							#this can be 6 per plot definition
        do_nPlot(nPlot, filenamesToPlot)

    try:
        fig.clf()
        plt.close(fig)
        if y1: del ax
        if y2: del ax2
    except:
        pass

    sendToLog(secMillis(d0)+" S.m  finished ..  after cleanup",level=1)
    xTime=[]
    columnDataToPlot=[]
    oldPLOT=copy.deepcopy(PLOT)
    return



def do_nPlot(nPlot,filenamesToPlot):
    global PLOT,oldPLOT, NOTdataFromTimeSeries
    global newData, plotDatastore
    global numberOfPlots,  noOfDays, numberOfMinutesInTimeBins, numberOfTimeTypes, numberOfTimeBins, dataColumnCount
    global indigoPlotDataDir, parameterFile, indigoPNGdir,indigoPath
    global myPID, msgCount, logHandle, quitNOW
    global plotSizeNames, plotTimeNames, timeDataNumbers, dataVersion, parameterVersion,debugEnable
    global xtimeCol, columnDataToPlot,  countTimeBinsMax, countTimeBinsWithDataMax, zeroYColumn
    global yMinL, yMinR, yMaxR, yMaxL, xMax, xMin, y1, y2, firstDaytoPlot, lastDaytoPlot, lastBinTime, colsToPlot, colsToPlotB,columnsToPlot, numberofNonTimeBins 
    global noOfMinutesInTimeBins, emptyBlanks, MHD, d0, d1, doPLOT, zeroYValue,  BordOff, Xfline1, Xfline2, xTime, DeviceNamePlotpng0
    global dataOffsetInTimeDataNumbers
    global eventData, eventIndex, DEVICE, dataColumnToDevice0Prop1Index
    
    try:
        #		print str(PLOT[nPlot]["NumberIsUsed"]) +" " +str(nPlot)+" " +str(numberOfPlots)
                plotN = PLOT[nPlot]
                if plotN["NumberIsUsed"] !=1: return
                if not( filenamesToPlot[0] =="" or filenamesToPlot[0] =="do all plots" or plotN["DeviceNamePlot"] in filenamesToPlot  ): return
        
                #### check if there is anything new in the PLOT definition
                doPLOT=False
        #		if  filenamesToPlot[0] =="" or filenamesToPlot[0] =="do all plots":
                if plotN["PlotType"] == "dataFromTimeSeries" and newData: doPLOT=True
        #		sendToLog("-- "+ plotN["DeviceNamePlot"]+" "+plotN["PlotType"] +"   newData "+str(newData),FULL=True,level=1 )

                if nPlot in oldPLOT:
                    if cmp(oldPLOT[nPlot],PLOT[nPlot]) !=0:
                        oldPLOT[nPlot]=copy.deepcopy(plotN)
                        sendToLog("-- oldplot!=newplot"+ plotN["DeviceNamePlot"],FULL=True,level=1 )
                        doPLOT=True
                    else:
                        sendToLog("-- oldplot==newplot"+ plotN["DeviceNamePlot"],FULL=True,level=1 )
                    if not doPLOT:				### check if plotfiles already exist, if not need to redo
                        for tType in range(numberOfTimeTypes):
                            if plotN["PlotType"] != "dataFromTimeSeries" and tType>0: continue
                            if plotN["PlotType"] == "dataFromTimeSeries" and plotN["MHDDays"][tType] ==0: continue
                            if plotN["PlotType"] == "dataFromTimeSeries":
                                DeviceNamePlotpng0= indigoPNGdir+plotN["DeviceNamePlot"]+"-"+plotTimeNames[tType]
                            else:
                                DeviceNamePlotpng0= indigoPNGdir+plotN["DeviceNamePlot"]
                            for ss in range(2):
                                if len(str(plotN["resxy"][ss]))>5:
                                    if not os.path.isfile(DeviceNamePlotpng0+"-"+plotSizeNames[ss]+".png"): doPLOT=True
                                    if not os.path.isfile(DeviceNamePlotpng0+"-"+plotSizeNames[ss]+".png"): doPLOT=True

                else:
                    oldPLOT[nPlot]=copy.deepcopy(PLOT[nPlot])
                    doPLOT=True
        #		else:
        #			doPLOT=True
            
                if not doPLOT:
                    sendToLog("-- no change in data and plot definition and files exist, skipping plotting: "+ plotN["DeviceNamePlot"],FULL=True,level=1 )
                    return


                if plotN["XScaleFormat"].find("%Y")>-1:
                    XisDate=True
                    if plotN["XScaleFormat"].find("+")>-1:
                        XformIN =plotN["XScaleFormat"].split("+")[0].strip('"')
                        Xformat =plotN["XScaleFormat"].split("+")[1].strip('"')
                        if Xformat.find("\\n") >-1:
                            Xfline1=Xformat.split("\\n")[0]
                            Xfline2=Xformat.split("\\n")[1]
                        else:
                            Xfline1=Xformat
                            Xfline2=Xformat=""
                    else:
                        XformIN =plotN["XScaleFormat"].strip('"')
                        Xformat =""
                        Xfline1=Xformat
                        Xfline2=Xformat=""
                else:
                    XisDate=False
                    XformIN =""
                    Xformat =""
                colsToPlot=0
                for ll in plotN["lines"]:
                    if plotN["lines"][ll]["lineToColumnIndexA"] !=0:colsToPlot+=1



                if len(plotN["LeftScaleRange"]) > 2:
                    yMinL= float(plotN["LeftScaleRange"].split(":")[0])
                    yMaxL= float(plotN["LeftScaleRange"].split(":")[1])
                else:
                    yMinL= -999999999999999999.
                    yMaxL=  999999999999999999.
                if len(plotN["RightScaleRange"]) > 2:
                    yMinR= float(plotN["RightScaleRange"].split(":")[0])
                    yMaxR= float(plotN["RightScaleRange"].split(":")[1])
                else:
                    yMinR= -999999999999999999.
                    yMaxR=  999999999999999999.
                if len(plotN["XScaleRange"]) > 2:
                    xMin= float(plotN["XScaleRange"].split(":")[0])
                    xMax= float(plotN["XScaleRange"].split(":")[1])
                else:
                    xMin= -999999999999999999.
                    xMax=  999999999999999999.

                if yMinL != -999999999999999999. :	zeroYValue = yMinL
                else:								zeroYValue = 0.0000001

                BordOff =["1","2","4","8"]
                try:
                    BordOff =plotN["Border"].split("+")
                except:
                    pass
                BorderColor=[plotN["TextColor"],plotN["TextColor"],plotN["TextColor"],plotN["TextColor"]]
                for i in range(4):
                    if BordOff[i] =="0":
                        BorderColor[i]=plotN["Background"]


                sendToLog(" ",level=1 )
                sendToLog("plotting ################:"+ str(nPlot)+"   -- plot: "+ plotN["DeviceNamePlot"]+"   -- compress PNG: "+ str(plotN["compressPNGfile"])+" ################",level=1 )

                colOffset = 1 + dataOffsetInTimeDataNumbers
                rows=0
                if plotN["PlotType"]!= "dataFromTimeSeries":
                    colOffset = 1 
                    numberofNonTimeBins=0
                    xTime=[]
                    zeroYColumn=[]
                    plotDatastore =[]
                    f=open(indigoPlotDataDir+"data/"+plotN["PlotFileOrVariName"],"r")
                    for line in f.readlines():
                        if len(line) < 2: continue  # skip junk lines
                        if line.find("#")==0: continue # skip first line
                        rows+=1
                        test = line.strip("\n").split(";")
                        test.insert(1,1)
                        plotDatastore.append(test)
                        xTime.append(float(test[0]))
                        zeroYColumn.append(zeroYValue)
                        numberofNonTimeBins+=1
                    f.close()
        #			sendToLog("plotDatastore "+ str(plotDatastore[:10]),1)
                    firstDaytoPlot = xMin
                    lastDaytoPlot  = xMax
                    DeviceNamePlotpng0= indigoPNGdir+plotN["DeviceNamePlot"]
                    # check if new data:
                    if plotN["DeviceNamePlot"] in NOTdataFromTimeSeries:
                        if comp(NOTdataFromTimeSeries[plotN["DeviceNamePlot"]],plotDatastore)!=0:
                            NOTdataFromTimeSeries[plotN["DeviceNamePlot"]]= copy.deepcopy(plotDatastore)
                            doPLOT=True
                    sendToLog("#c:"+unicode(colsToPlot)+"; grid:"+plotN["Grid"]+"; 0Ln:"+str(plotN["drawZeroLine"])+"-   doPlot: "+ str(doPLOT)+" rows: "+str(rows)+ "   Border Color: "+ str(BorderColor)+"   Background Color: "+ plotN["Background"],level=1)
                else:
                    sendToLog("#c:"+unicode(colsToPlot)+"; grid:"+plotN["Grid"]+"; 0Ln:"+str(plotN["drawZeroLine"])+"-   doPlot: "+ str(doPLOT)+ "   Border Color: "+ str(BorderColor)+"   Background Color: "+ plotN["Background"],level=1 )
                ## show border or not

        #		t1 = time.time()
                for tType in range(0,numberOfTimeTypes):					# this is for the day/hour/minute names
                    do_PlottType( plotN, filenamesToPlot, XisDate, tType,colOffset, BorderColor)

    except  Exception, e:
        sendToLog("Line '%s' has error='%s'" % (sys.exc_traceback.tb_lineno, e),1)
    ## end of plot loop

                    
def do_PlottType( plotN, filenamesToPlot, XisDate, tType,colOffset, BorderColor):


    anyData = do_prepData( plotN, filenamesToPlot, XisDate, tType,colOffset, BorderColor)

    if anyData>0: do_DisplayData( plotN, filenamesToPlot, XisDate, tType,colOffset, BorderColor)



def do_prepData( plotN, filenamesToPlot, XisDate, tType,colOffset, BorderColor):
    global PLOT,oldPLOT, NOTdataFromTimeSeries
    global newData, plotDatastore, weightDataToPlot
    global numberOfPlots,  noOfDays, numberOfMinutesInTimeBins, numberOfTimeTypes, numberOfTimeBins, dataColumnCount
    global indigoPlotDataDir, parameterFile, indigoPNGdir,indigoPath
    global myPID, msgCount, logHandle, quitNOW
    global plotSizeNames, plotTimeNames, timeDataNumbers, dataVersion, parameterVersion,debugEnable
    global xtimeCol, columnDataToPlot,  countTimeBinsMax, countTimeBinsWithDataMax, zeroYColumn
    global yMinL, yMinR, yMaxR, yMaxL, xMax, xMin, y1, y2, firstDaytoPlot, lastDaytoPlot, lastBinTime, colsToPlot, colsToPlotB,columnsToPlot, numberofNonTimeBins 
    global noOfMinutesInTimeBins, emptyBlanks, MHD, d0, d1, doPLOT, zeroYValue,  BordOff, Xfline1, Xfline2, xTime, DeviceNamePlotpng0
    global eventData, eventIndex,eventType, DEVICE, dataColumnToDevice0Prop1Index

    anyData = 0

    try:
        if  plotN["PlotType"] != "dataFromTimeSeries" and tType>0: return

        if  plotN["PlotType"] == "dataFromTimeSeries":
            if 	plotN["MHDDays"][tType] ==0: return
            plotDatastore =timeDataNumbers[tType][:]
            xTime=[]
            zeroYColumn=[]
            for ii in range(numberOfTimeBins[tType]):
                dtString =plotDatastore[ii][0]
                xTime.append(datetime.datetime(int(dtString[0:4]),int(dtString[4:6]),int(dtString[6:8]),int(dtString[8:10]),int(dtString[10:12]),0))
                zeroYColumn.append(zeroYValue)
            lastBinTime=plotDatastore[len(plotDatastore)-1][0]
            firstDaytoPlot = 0
            lastDaytoPlot  = 0

            firstDaytoPlot, lastDaytoPlot = firstLastDayToPlot(int(plotN["MHDDays"][tType]), int(plotN["MHDShift"][tType]), tType)

            DeviceNamePlotpng0= indigoPNGdir+plotN["DeviceNamePlot"]+"-"+plotTimeNames[tType]

        if XisDate:
            xTime=[]
            zeroYColumn=[]
            for ii in range(1,numberofNonTimeBins):
                dtString =plotDatastore[ii][0]
                xTime.append(datetime.datetime(int(dtString[0:4]),int(dtString[4:6]),int(dtString[6:8]),int(dtString[8:10]),int(dtString[10:12])))
                zeroYColumn.append(zeroYValue)
            DeviceNamePlotpng0= indigoPNGdir+plotN["DeviceNamePlot"]
            first = plotDatastore[1][0]
            last  = plotDatastore[len(plotDatastore)-1][0]
            firstDaytoPlot = datetime.datetime(int(first[0:4]),int(first[4:6]),int(first[6:8]),int(first[8:10]),int(first[10:12]))
            lastDaytoPlot =  datetime.datetime(int(last[0:4]) ,int(last[4:6]) ,int(last[6:8]) ,int(last[8:10]) ,int(last[10:12]),59)
            lastBinTime=last
        y1=False
        y2=False
        columnsToPlot  =[]
        columnsToPlotB =[]
        colsToPlot =0
        colsToPlotB =0
        for lli in range(0,100):  # this way we have it generated in sequence if we dor for ll in plot[nPlot][lines]  it is random
            ll = str(lli)
            if ll not in plotN["lines"]: continue
            if plotN["lines"][ll]["lineToColumnIndexA"] !=0:
                theCol = int(plotN["lines"][ll]["lineToColumnIndexA"])
                columnsToPlot.append([theCol,ll])
                if plotN["lines"][ll]["lineLeftRight"] == "Right": y2=True
                else:											   y1=True
                colsToPlot+=1
                if plotN["lines"][ll]["lineToColumnIndexB"] !=0:
                    columnsToPlotB.append([int(plotN["lines"][ll]["lineToColumnIndexB"]),ll])
                else:
                    columnsToPlotB.append([0,0])
            
        columnDataToPlot  = [[] for ii in range(colsToPlot)]
        xtimeCol		  = [[] for ii in range(colsToPlot)]
        weightDataToPlot  = [[] for ii in range(colsToPlot)]
        countTimeBinsMax  = 0
        countTimeBinsWithDataMax=0
        countP=0


        if  plotN["XYvPolar"] =="xy":

                xtimeForOneCol=[]
                for col in range(colsToPlot):
                            colToPlot = copy.deepcopy(columnsToPlot)
                            colToPlotB = copy.deepcopy(columnsToPlotB)
                            lCol = colToPlot[col][1]
                            try:    mul = float(plotN["lines"][lCol]["lineMultiplier"])
                            except: mul =1.
                            try:    off = float(plotN["lines"][lCol]["lineOffset"])
                            except: off =0.

                            leftRange = plotN["lines"][lCol]["lineOffset"]
                            fromTo = ""
                            if "lineFromTo" in plotN["lines"][lCol]:
                                fromTo = plotN["lines"][lCol]["lineFromTo"]
                            lineShift=int(plotN["lines"][lCol]["lineShift"])
                            xtimeForOneCol  = []
                            theColumnValues = []
                            weight			= []
                            firstData       = False
                            countTimeBins   = 0
                            dataCol         = colToPlot[col][0]
                            XT              = []
                            countTimeBinsWithData=0
                            #sendToLog(plotN["DeviceNamePlot"]+ " dataCol: "+ str(dataCol)+ " lcol: "+ str(lCol)+" col: "+ str(col)+"  colToPlot: "+str(colToPlot[col]), level=1) 
                            if  plotN["PlotType"] == "dataFromTimeSeries" and str(dataCol) in eventIndex:
                                    evD = eventData[str(dataCol)]
                                    resetType = eventType[str(dataCol)].split("-")[1] ##reset = day/week/month/year/bin
                                    showZero  = eventType[str(dataCol)].split("-")[2]=="zero" ## show  zero bins
                                    evType    = eventType[str(dataCol)].split("-")[0] 
                                    nData     = eventIndex[str(dataCol)]
                                    dataToPlot=[]
                                    #sendToLog("count  eventType:"+unicode(eventType[str(dataCol)]),level=1)
                                    #XisDate =True
                                    if   evType == "down":
                                        for nn in range(nData):
                                            if float(evD[nn][7]) ==0.:
                                                dataToPlot.append(copy.deepcopy(evD[nn])) 
                                                XT.append(datetime.datetime.strptime(evD[nn][0], "%Y%m%d%H%M%S"))
                                        nBins =len(XT)
                                    elif evType == "up":
                                        for nn in range(nData):
                                            try:
                                                if float(evD[nn][7]) >0.:
                                                    dataToPlot.append(copy.deepcopy(evD[nn]))  
                                                    XT.append(datetime.datetime.strptime(evD[nn][0], "%Y%m%d%H%M%S"))
                                            except:
                                                sendToLog(str(nn) + " "+unicode(evD),level=1)
                                                break
                                        nBins =len(XT)
                                    elif evType == "change":
                                        last=""
                                        for nn in range(nData):
                                            if evD[nn][7] !=last:
                                                last=evD[nn][7] 
                                                dataToPlot.append(copy.deepcopy(evD[nn]))  
                                                XT.append(datetime.datetime.strptime(evD[nn][0], "%Y%m%d%H%M%S"))
                                        nBins =len(XT)
                                    elif evType == "count":
                                    
                                        nb                = 0
                                        currentBinDate    = xTime[nb]
                                        currentBinDateSTR = currentBinDate.strftime("%Y%m%d%H%M%S")
                                        nextBinDate       = xTime[nb+1]
                                        nextBinDateSTR    = nextBinDate.strftime("%Y%m%d%H%M%S")
                                        firstBinDateSTR   = currentBinDateSTR
                                        lastBinDateSTR    = currentBinDateSTR
                                        lasteventData     = evD[0]
                                        firstEventInRange = False
                                        #sendToLog("count  firstBinDate:"+firstBinDateSTR+"  "+evType+" "+resetType+" "+unicode(showZero)+" nData:"+unicode(nData),level=1)
                                        for nn in range(nData):
                                            lasteventData = copy.deepcopy(evD[max(0,nn-1)])
                                            currdateINSTR = copy.deepcopy(evD[nn][0])
                                            currdateIN    = datetime.datetime.strptime(currdateINSTR, "%Y%m%d%H%M%S")

                                            if currdateINSTR < firstBinDateSTR: continue
                                            if not firstEventInRange:
                                                sendToLog("count  firstBinDate found :"+unicode(lasteventData)+"  "+ str(nn),level=1)
                                                dataToPlot.append([currentBinDateSTR,1,0,0,0,0,1,0])
                                                XT.append(currentBinDate)
                                            firstEventInRange = True
                                            

                                            reset = False
                                            if currdateINSTR > nextBinDateSTR:
                                                if nb+1 >= len(xTime): break
                                                nb               += 1
                                                lastBinDateSTR    = currentBinDateSTR
                                                currentBinDate    = nextBinDate
                                                currentBinDateSTR = nextBinDateSTR
                                                nextBinDate       = xTime[nb]
                                                nextBinDateSTR    = nextBinDate.strftime("%Y%m%d%H%M%S")
                                                while currdateINSTR > nextBinDateSTR:
                                                    if nb+1 >= len(xTime): break
                                                    nb               += 1
                                                    lastBinDateSTR    = currentBinDateSTR
                                                    currentBinDate    = nextBinDate
                                                    currentBinDateSTR = nextBinDateSTR
                                                    nextBinDate       = xTime[nb]
                                                    nextBinDateSTR    = nextBinDate.strftime("%Y%m%d%H%M%S")
                                                    if currdateINSTR  < currentBinDateSTR: continue
                                                    if currdateINSTR  < nextBinDateSTR:    continue
                                                    if showZero:
                                                        if resetType == "bin":                                  reset = True
                                                        if lastBinDateSTR[0:8] != currdateINSTR[0:8]: 
                                                            if resetType == "day":                              reset = True
                                                            if resetType == "week"  and dataToPlot[-1][2] == 6: reset = True
                                                            if resetType == "month" and dataToPlot[-1][3] == 1: reset = True
                                                            if resetType == "year"  and dataToPlot[-1][4] == 1: reset = True
                                                    if nn > 0 and reset:
                                                        if evD[nn-1][-1] ==0:
                                                            dataToPlot.append([evD[nn-1][0],1,0,0,0,0,1,0])
                                                            XT.append(datetime.datetime.strptime(evD[nn-1][0], "%Y%m%d%H%M%S"))

                                                if resetType == "bin":                           reset = True
                                                if lastBinDateSTR[0:8] != currdateINSTR[0:8]: 
                                                    if resetType == "day":                       reset = True
                                                    if resetType == "week"  and  evD[nn][2] ==6: reset = True
                                                    if resetType == "month" and  evD[nn][3] ==1: reset = True
                                                    if resetType == "year"  and  evD[nn][4] ==1: reset = True
                                                    
                                                XT.append(currentBinDate)
                                                dataToPlot.append(copy.deepcopy(evD[nn]))  
                                                if reset:
                                                    if float(evD[nn][-1]) > 0.:
                                                        dataToPlot[-1][-1] = 1 
                                                    else:
                                                        dataToPlot[-1][-1] = 0
                                                else:
                                                    if len(dataToPlot) > 1:
                                                        dataToPlot[-1][-1] += dataToPlot[-2][-1]

                                            else:
                                                if float(evD[nn][-1]) >0.:
                                                    dataToPlot[-1][-1] += 1 
                                            #if tType ==2: print  nn,  tType, col, currentBinDateSTR,reset ,evD[nn], dataToPlot[-1][-1]
                                                     
                                            #print currdateIN, currentBinDate, dataToPlot[-1], evD[-1], XT[-1]
                                        nBins =len(XT)
                                        #sendToLog("count nBins "+unicode(nBins),level=1)
                                        #sendToLog("count dataToPlot "+unicode(dataToPlot[0:100]),level=1)
                                        #sendToLog("count XT  "+unicode(XT[0:100]),level=1)

                                    else:
                                        dataToPlot = copy.deepcopy(evD)
                                        nBins =eventIndex[str(dataCol)]
                                        for nn in range(nBins): 
                                            XT.append(datetime.datetime.strptime(evD[nn][0], "%Y%m%d%H%M%S"))
                                    #sendToLog("count "+unicode(nBins) +"  "+unicode(len(dataToPlot))+"  "+unicode(len(XT)),level=1)
                                    
                                    colToPlot[col][0]   = 1
                                    colToPlotB[col][0]  = 0
                                    colToPlotB[col][1]  = 0
                                    #sendToLog(" lcol: "+ str(lCol)+   " XT: " + str(XT)[0:100], level=1) 
                                    #if tType ==2: print firstBinDateSTR,nBins,len(dataToPlot),len(xTime), col,"\n", XT[0],XT[-10:-1],"\n", dataToPlot[0], dataToPlot[-10:-1]
                            else:
                                XT = xTime
                                dataToPlot = plotDatastore
                                if  plotN["PlotType"] == "dataFromTimeSeries":
                                    nBins =numberOfTimeBins[tType]
                                else:
                                    nBins = min(numberofNonTimeBins, len(XT))

                            lR = plotN["lines"][lCol]["lineEveryRepeat"]
                            try:
                                lRi=int(lR)
                            except:
                                lRi=""
                                
                            #sendToLog(" col "+ str(lCol) + " lCol " + str(lCol)+  "  nBins" + str(nBins), level=1) 
                            for jj in range(nBins):
                                        yIsText=False
                                        shiftedTime = XT[jj]
                                        if plotN["PlotType"] == "dataFromTimeSeries" or XisDate:
                                                if lineShift > 0: shiftedTime += datetime.timedelta(lineShift)
                                                try:
                                                    if shiftedTime  < firstDaytoPlot: continue
                                                except:
                                                    sendToLog("shiftedTime: "+ str(shiftedTime) +"  firstDaytoPlot:"+ str(firstDaytoPlot)  )
                                                    continue
                                                if shiftedTime  > lastDaytoPlot : continue
                                                shifttimeString = shiftedTime.strftime("%Y%m%d%H%M%S")
                                                if fromTo.find(":") >0:
                                                        fT=fromTo.split(":")
                                                        shifttimeString1= shifttimeString[0:len(fT[0])]
                                                        ##sendToLog("shift: "+ unicode(shiftedTime)+ " "+ unicode(shifttimeString1)+"  "+ unicode(fT))
                                                        if shifttimeString1  < fT[0]: continue
                                                        if shifttimeString1  > fT[1]: continue
                                        else:
                                            try:
                                                if float(firstDaytoPlot) - float(shiftedTime) > 0.: continue
                                            except:
                                                sendToLog(" error at  col "+ str(col) +"  XisDate "+str(XisDate)+"  PlotType "+str(plotN["PlotType"])+"  firstDaytoPlot "+str(firstDaytoPlot)+"  shiftedTime "+str(shiftedTime), level=1) 
                                                continue        

                                        if dataToPlot[jj][0].find("#") ==0: continue# skip comment lines
                                        #sendToLog("step1 "+ unicode(dataToPlot[jj][1])+ " "+unicode(dataToPlot[jj][colToPlot[col][0]+colOffset]),level=1)

                                        countTimeBins+=1
                                        if plotN["PlotType"] == "dataFromTimeSeries" and colToPlot[col][0] < 0:
                                            yyy=float(countTimeBinsWithData*(mul-off)) ## for straight line 
                                            theColumnValues.append(yyy) ## for straight line 
                                            xtimeForOneCol.append(shiftedTime)
                                            countTimeBinsWithData+=1
                                            continue
                                        
                                        suppressPoint = 0
                                        if float(dataToPlot[jj][1]) > 0:
                                            if lR != "1":

                                                if lRi !="" and jj%lRi !=0:
                                                    suppressPoint = 1
                            
                                                elif  lR =="evenMinutes" and int(shifttimeString[11:12])%2 == 1:
                                                    suppressPoint = 2
                                                elif  lR =="oddMinutes"  and int(shifttimeString[11:12])%2 == 0:
                                                    suppressPoint = 2
                                                elif  lR =="evenHours"   and int(shifttimeString[9:10])%2 == 1:
                                                    suppressPoint = 2
                                                elif  lR =="oddHours"    and int(shifttimeString[9:10])%2 == 0:
                                                    suppressPoint = 2
                                                elif  lR =="evenDays"    and int(shifttimeString[7:8])%2 == 1:
                                                    suppressPoint = 2
                                                elif  lR =="oddDays"     and int(shifttimeString[7:8])%2 == 0:
                                                    suppressPoint = 2
                                                elif  lR =="evenMonths"  and int(shifttimeString[4:5])%2 == 1:
                                                    suppressPoint = 2
                                                elif  lR =="oddMonths"   and int(shifttimeString[4:5])%2 == 0:
                                                    suppressPoint = 2

                                                elif  lR == "lastBinOfMonth" and str(dataToPlot[jj][3])  == "0": suppressPoint = 2
                                                elif  lR == "lastBinOfYear"  and str(dataToPlot[jj][4])  == "0": suppressPoint = 2


                                                elif  lR.find("weekDay") == 0:
                                                    if  lR.find("Last") >- 1:
                                                        if   tType == 0   and shifttimeString[8:12] != "2355":
                                                            suppressPoint = 1
                                                        elif tType == 1   and shifttimeString[8:10]  != "23":    
                                                            suppressPoint = 1
                                                    try:
                                                            int(lR[7:8])
                                                            if  str(dataToPlot[jj][2])  != lR[7:8]:
                                                                suppressPoint = 2
                                                    except:
                                                        pass

                                                elif    lR.find("hour") == 0:
                                                    if  tType != 2:
                                                        if  lR.find("Last") > -1:
                                                            if   tType == 0   and shifttimeString[10:12] != "55":
                                                                suppressPoint = 2
                                                        try: 
                                                            HH = lR[4:6]
                                                            int(HH)
                                                            if shifttimeString[8:10]  !=  HH:
                                                                suppressPoint = 1
                                                        except:
                                                            pass
                                                    ##sendToLog(lR + "  "+ str(shifttimeString)+ " "+ str(suppressPoint) )
                                                
                                            
                                            
                                                #sendToLog(lR + " 8: "+ str(dataToPlot[jj][8])+"  9:"+ str(dataToPlot[jj][9]),level=1)
                                                #sendToLog(lR + " ok "+ str(dataToPlot[jj][colToPlot[col][0]+colOffset]))
                                            if suppressPoint ==2:  
                                                yy = None ; theValue = None 
                                            elif  suppressPoint ==1:
                                                continue   
                                            else: 
                                                try:
                                                    yy = float(dataToPlot[jj][colToPlot[col][0]+colOffset])
                                                except:
                                                    if plotN["PlotType"] == "dataFromTimeSeries":                                                                            
                                                        continue
                                                    yy = dataToPlot[jj][colToPlot[col][0]+colOffset]
                                                    yIsText=True   
                                            
                                            if  plotN["PlotType"] == "dataFromTimeSeries":
                                                if yy !="" and yy != None : firstData=True
                                                if not firstData: continue	# skip first sets of data if there is nothing, need at least one !=0 number to start
                                            if yIsText:   
                                                theValue=yy
                                            elif yy != None:      
                                                theValue= yy*mul+off
                                            countTimeBinsWithData+=1
                                            #sendToLog("step3",level=1)

                                            if colToPlotB[col][1] !=0:
                                                if not yIsText:
                                                   if suppressPoint>0:  
                                                        yy = None 
                                                        theValue = yy
                                                        weight.append(yy)
                                                   else:
                                                        try:
                                                            yy = float(dataToPlot[jj][colToPlotB[col][0]+colOffset])
                                                        except:
                                                            yy=0.0
                                                        if plotN["lines"][lCol]["lineFunc"] =="+":		theValue = theValue + ( yy*mul+off )
                                                        elif plotN["lines"][lCol]["lineFunc"] =="-": 	theValue = theValue - ( yy*mul+off )
                                                        elif plotN["lines"][lCol]["lineFunc"] =="*": 	theValue = theValue * ( yy*mul+off )
                                                        elif plotN["lines"][lCol]["lineFunc"] =="/":
                                                            if yy*mul+off ==0.: 	theValue = 0.
                                                            else:					theValue = theValue / ( yy*mul+off )
                                                        elif (plotN["lines"][lCol]["lineFunc"] =="C" or
                                                              plotN["lines"][lCol]["lineFunc"] =="E" or
                                                              plotN["lines"][lCol]["lineFunc"] =="S" ) :
                                                              weight.append(yy)

                                            if suppressPoint<1: 
                                                if plotN["lines"][lCol]["lineType"].find("DOT")==0:
                                                    if plotN["lines"][lCol]["lineLeftRight"] == "Right":	
                                                        if theValue>  yMaxR or theValue <yMinR: continue
                                                    else:
                                                        if theValue>  yMaxL or theValue <yMinL: continue
                                                else:
                                                    if plotN["lines"][lCol]["lineLeftRight"] == "Right":	
                                                        theValue = max(yMinR,min(yMaxR,theValue))
                                                    else:
                                                        theValue = max(yMinL,min(yMaxL,theValue))

                                            theColumnValues.append(theValue)
                                            xtimeForOneCol.append(shiftedTime)
                            #if lR =="oddHours" or lR =="evenHours":
                            #    sendToLog(lR+ " theColumnValues "+ str(theColumnValues) + " xtimeForOneCol " + str(xtimeForOneCol), level=1) 
                        
                            countTimeBinsMax=max(countTimeBinsMax, countTimeBins)
                            countTimeBinsWithDataMax=max(countTimeBinsWithDataMax, countTimeBinsWithData)

                            if plotN["PlotType"] == "dataFromTimeSeries" and colToPlot[col][0] < 0:
                                for ii in range(len(theColumnValues)):
                                    theColumnValues[ii]= theColumnValues[ii]/max(1.,float(countTimeBinsWithData))+off

                            if len(theColumnValues) ==0:
                                    sendToLog("theColumnValues ==[] = no data for tType "+str(tType)+ ";    column: " +str(col),level=1 )
                                    out =""
                                    start= max(len(dataToPlot) -10,0)
                                    for ii in range(start,len(dataToPlot)):
                                        out += str(dataToPlot[ii][0])+"-"+str(dataToPlot[ii][colToPlot[col][0]+colOffset])+"\n"
                                    sendToLog("last 10 records:\n"+out,level=1)
                                    continue

                            smooth= plotN["lines"][lCol]["lineSmooth"]
                            if smooth=="combine3Bins":
                                        numbersToPlotY=[]
                                        nX =len(xtimeForOneCol)
                                        for mm in range(2,nX+2,3):
                                            try:
                                                ave =(theColumnValues[min(nX-1,mm-2)]+theColumnValues[min(nX-1,mm-1)]+theColumnValues[min(nX-1,mm)])/3
                                            except:
                                                sendToLog( u" error "+ str(theColumnValues[min(nX-1,mm-2)])+"--"+str(theColumnValues[min(nX-1,mm-1)])+"--"+str(theColumnValues[min(nX-1,mm)])+"--", 1)
                                                ave =(theColumnValues[min(nX-1,mm)])
                                            if len(numbersToPlotY) < nX: numbersToPlotY.append(ave)
                                            if len(numbersToPlotY) < nX: numbersToPlotY.append(ave)
                                            if len(numbersToPlotY) < nX: numbersToPlotY.append(ave)
                                        theColumnValues=copy.deepcopy(numbersToPlotY)
                            elif smooth=="average3Bins":
                                        numbersToPlotY=[]
                                        nX =len(xtimeForOneCol)
                                        try:
                                                ave =(theColumnValues[0]+theColumnValues[1])/2
                                        except:
                                                ave =(theColumnValues[0])
                                        numbersToPlotY.append(ave)
                                        for mm in range(1,nX-1):
                                            try:
                                                ave =(theColumnValues[mm-1]+theColumnValues[mm]+theColumnValues[mm+1])/3.
                                            except:
                                                ave =(theColumnValues[mm])
                                            numbersToPlotY.append(ave)
                                        try:
                                                ave =(theColumnValues[nX-2]+theColumnValues[nX-1])/2
                                        except:
                                                ave =(theColumnValues[nX-1])
                                        numbersToPlotY.append(ave)

                            elif smooth=="trailingAverage":
                                        numbersToPlotY=[]
                                        nX =len(xtimeForOneCol)
                                        numbersToPlotY.append(theColumnValues[0])
                                        numbersToPlotY.append((theColumnValues[1]+theColumnValues[0])/2)
                                        numbersToPlotY.append((theColumnValues[2]+theColumnValues[1]+theColumnValues[0])/3)
                                        numbersToPlotY.append((theColumnValues[3]+theColumnValues[2]+theColumnValues[1]+theColumnValues[0])/4)
                                        for mm in range(4,nX):
                                            try:
                                                numbersToPlotY.append((theColumnValues[mm-4]+theColumnValues[mm-3]+theColumnValues[mm-2]+theColumnValues[mm-1]+theColumnValues[mm])/5)
                                            except:
                                                numbersToPlotY.append(theColumnValues[mm])
                                        theColumnValues=copy.deepcopy(numbersToPlotY)



                            lR = plotN["lines"][lCol]["lineEveryRepeat"]
                            if lR!="1":
                                    nW=len(weight)
                                    numbersToPlotX=[];numbersToPlotY=[];numbersWeight=[]
                                    nX =len(xtimeForOneCol)

                                    if lRi !="":
                                        for mm in range(nX):
                                            if mm%lRi==0:
                                                numbersToPlotX.append(xtimeForOneCol[mm])
                                                numbersToPlotY.append(theColumnValues[mm])
                                                if nW>0: numbersWeight.append(weight[mm])
                                            theColumnValues=copy.deepcopy(numbersToPlotY)
                                            xtimeForOneCol=copy.deepcopy(numbersToPlotX)
                                            if nW>0: weight=copy.deepcopy(numbersWeight)

                                    elif lR=="firstBin":
                                        xtimeForOneCol= [xtimeForOneCol[0]]
                                        theColumnValues= [theColumnValues[0]]
                                        if nW>0: weight=[weight[0]]

                                    elif lR=="lastBin":  # only last bin with data
                                        xtimeForOneCol=[xtimeForOneCol[-1]]
                                        theColumnValues=[theColumnValues[-1]]
                                        if nW>0: weight = [weight[-1]]

                                    elif lR=="rightY":  # use last bin with data at y right
                                        xtimeForOneCol=[lastDaytoPlot]
                                        theColumnValues=[theColumnValues[-1]]


                                    elif lR=="min":
                                        xtimeForOneCol,theColumnValues,weight = getminMaxPerTimeperiod(-1,""  ,xtimeForOneCol,theColumnValues,weight)
                                    elif lR=="max":
                                        xtimeForOneCol,theColumnValues,weight = getminMaxPerTimeperiod(+1,""  ,xtimeForOneCol,theColumnValues,weight)

                                    elif lR=="minHour" and tType < 1:
                                        xtimeForOneCol,theColumnValues,weight = getminMaxPerTimeperiod(-1,"%H",xtimeForOneCol,theColumnValues,weight)
                                    elif lR=="maxHour" and tType < 1:
                                        xtimeForOneCol,theColumnValues,weight = getminMaxPerTimeperiod(+1,"%H",xtimeForOneCol,theColumnValues,weight)

                                    elif lR=="minDay" and tType < 2:
                                        xtimeForOneCol,theColumnValues,weight = getminMaxPerTimeperiod(-1,"%d",xtimeForOneCol,theColumnValues,weight)
                                    elif lR=="maxDay" and tType < 2:
                                        xtimeForOneCol,theColumnValues,weight = getminMaxPerTimeperiod(+1,"%d",xtimeForOneCol,theColumnValues,weight)

                                    elif lR=="minMonth":
                                        xtimeForOneCol,theColumnValues,weight = getminMaxPerTimeperiod(-1,"%m",xtimeForOneCol,theColumnValues,weight)
                                    elif lR=="maxMonth":
                                        xtimeForOneCol,theColumnValues,weight = getminMaxPerTimeperiod(+1,"%m",xtimeForOneCol,theColumnValues,weight)




                            # line smoothing with cspline
                            #					if nPlot== "944299738":
                            #						sendToLog(str(theColumnValues),level=1)
                            #						sendToLog(str(xtimeForOneCol),level=1)

                            #for smooth factor:
                            #s : float
                            #   A smoothing condition. The amount of smoothness is determined by satisfying the conditions: sum((w * (y - g))**2,axis=0) <= s where g(x) is the smoothed interpolation of (x,y). The user can use s to control the tradeoff between closeness and smoothness of fit. Larger s means more smoothing while smaller values of s indicate less smoothing. Recommended values of s depend on the weights, w. If the weights represent the inverse of the standard-deviation of y, then a good s value should be found in the range (m-sqrt(2*m),m+sqrt(2*m)) where m is the number of datapoints in x, y, and w. default : s=m-sqrt(2*m) if weights are supplied. s = 0.0 (interpolating) if no weights are supplied.
                            # so for m= 1000, 	s = ~1000 +-45
                            # so for m= 200, 	s = ~200 +-20


                            # not using:  spline  http://docs.scipy.org/doc/scipy/reference/tutorial/interpolate.html
                            # using:  spline  http://docs.scipy.org/doc/scipy-0.13.0/reference/generated/scipy.interpolate.splrep.html#scipy.interpolate.splrep
                            # not using:  spline  http://docs.scipy.org/doc/scipy/reference/tutorial/interpolate.html
                            #						makeSpline = scipy.interpolate.UnivariateSpline (xx, theColumnValues, s=200.0 )
                            #					sendToLog( u" xtimeForOneCol 0-10"+ str(xtimeForOneCol[:10]), 1)


                            if  (  plotN["lines"][lCol]["lineSmooth"] =="soft"
                                or plotN["lines"][lCol]["lineSmooth"] =="medium"
                                or plotN["lines"][lCol]["lineSmooth"] =="strong" ):

                                if    plotN["lines"][lCol]["lineSmooth"] =="strong"    : smooth = 1200.
                                elif  plotN["lines"][lCol]["lineSmooth"] == "medium" :   smooth = 200.
                                elif  plotN["lines"][lCol]["lineSmooth"] == "soft" :     smooth = 30.
                                else :                                                   smooth = 50.

                                if   len(xtimeForOneCol) >  600 : multi = 1
                                elif len(xtimeForOneCol) >  300 : multi = 2
                                elif len(xtimeForOneCol) >  150 : multi = 3
                                elif len(xtimeForOneCol) >   50 : multi = 8
                                else :                            multi = 15
                                if  plotN["PlotType"] == "dataFromTimeSeries":
        
                                    extraX = (time.mktime(xtimeForOneCol[1].timetuple()) - time.mktime(xtimeForOneCol[0].timetuple()))/ multi
    
                                xx = [] # for fitting if we add bins in seconds
                                xx1= [] # for fitting in seconds
                                xxT= [] # after fitting in datetime format for plotting
                                for tBins1 in range(len(xtimeForOneCol)):			# sciopy interpolate needs float
                                    if  plotN["PlotType"] == "dataFromTimeSeries":
                                        xx0 = time.mktime(xtimeForOneCol[tBins1].timetuple())   # converted to seconds
                                        xx.append(xx0)  # converted to seconds
                                        xx1.append(xx0)  # converted to seconds
                                        xxT.append(xtimeForOneCol[tBins1])  # converted to seconds
                                        if multi >1 and tBins1 < len(xtimeForOneCol)-1:
                                            for iMULT in range(1, multi):
                                                tt= xx0 +extraX*iMULT  # this is in seconds
                                                xx.append(tt)
                                                xxT.append(datetime.datetime.fromtimestamp(tt))  # back to date time
                                    else:
                                        xx0 = xtimeForOneCol[tBins1]
                                        xx.append(xx0)
                                        xx1.append(xx0)
                                        xxT.append(xtimeForOneCol[tBins1])  # converted to seconds
                                        if multi >1 and tBins1 < len(xtimeForOneCol)-1:
                                            extraX = (xtimeForOneCol[tBins1+1] - xtimeForOneCol[tBins1])/ multi
                                            for iMULT in range(1, multi):
                                                tt= xx0 +extraX*iMULT  # this is in seconds
                                                xx.append(tt)
                                                xxT.append(tt)
                                try:
                                    splineParams, fp,ier,msg= scipy.interpolate.splrep (xx1, theColumnValues, k=3, s=smooth , full_output=1)  #  smooth factor 50  least smoothing
                                    sendToLog( u" smoothing plot: \""+ plotN["TitleText"]+"\" line# " + str(lCol)+", ierr:"+ str(ier)+", msg: "+str(msg), 1)
                                    sendToLog( u" smoothing plot: fp "+ str(fp), 1)
                                    yy = scipy.interpolate.splev(xx,splineParams)  # y values
                                    yyL = len(yy)
                                    yyNAM = str(yy).count("nan")
                                except  Exception, e:
                                    sendToLog("interpolate '%s' has error='%s'" % (sys.exc_traceback.tb_lineno, e),0)
                                    yyL =0
                                    yyNAM =5
                                if yyL<=yyNAM:
                                    sendToLog( u" error smoothing plot: \""+ plotN["TitleText"]+"\" line# " + str(lCol)+" not suited for smoothing, either data not consecutive, or too steep, switched parameter to non-smooth" , 0)
                                    plotN["lines"][lCol]["lineSmooth"] ="None"
                                    xtimeCol[col]         = xtimeForOneCol
                                    columnDataToPlot[col] = theColumnValues
                                else:
                                    columnDataToPlot[col] =yy  # y values
                                    xtimeCol[col]=xxT  # x values

                                splineParams=""
                                yy =""
                                xxt=""
                                xx=""
                                xx1=""
                            else:
                                xtimeCol[col]         = xtimeForOneCol
                                columnDataToPlot[col] = theColumnValues
                                weightDataToPlot[col] = weight



        else:   # polar plot
                firstDaytoPlot =0
                if  plotN["PlotType"] == "dataFromTimeSeries":
                    if   tType ==2 :	firstDaytoPlot = float((datetime.date.today() - datetime.timedelta(int(plotN["MHDDays"][tType]))).strftime("%Y%m%d")+"000000"    )
                    elif tType ==1 :	firstDaytoPlot = float((datetime.date.today() - datetime.timedelta(int(plotN["MHDDays"][tType]))).strftime("%Y%m%d%H")+"0000"  )
                    elif tType ==0 : 	firstDaytoPlot = float((datetime.date.today() - datetime.timedelta(int(plotN["MHDDays"][tType]))).strftime("%Y%m%d%H%M")+"00")
                    nBins	=numberOfTimeBins[tType]
                else:nBins	=numberofNonTimeBins

                for col in range(colsToPlot):
                            lCol = columnsToPlot[col][1]
                            mul = plotN["lines"][lCol]["lineMultiplier"]
                            off = plotN["lines"][lCol]["lineOffset"]
                            xtimeForOneCol=[]
                            theColumnValues =[]
                            firstData=False
                            countTimeBinsWithData=0
                            countTimeBins=0

                            for ii in range(nBins):
                                        if  plotN["PlotType"] == "dataFromTimeSeries" and firstDaytoPlot >= float(plotDatastore[ii][0]): continue
                                        countTimeBins+=1
                                        if 	float(plotDatastore[ii][1]) > 0:
                                            countTimeBinsWithData+=1
                                            try:
                                                yy = float(plotDatastore[ii][columnsToPlot[col][0]+colOffset])
                                            except:
                                                yy=0.0
                                            theValue= yy*mul+off
                                            if  plotN["PlotType"] == "dataFromTimeSeries":
                                                try:
                                                    if float(plotDatastore[ii][columnsToPlotB[col][0]+colOffset]) !=0. and theValue !=0.:
                                                        xtimeForOneCol.append(float(plotDatastore[ii][columnsToPlotB[col][0]+colOffset]))
                                                        theColumnValues.append(theValue)
                                                except:
                                                    pass
                                            else:
                                                try:
                                                    if float(plotDatastore[ii][0]) !=0. and theValue !=0.:
                                                        xtimeForOneCol.append(float(plotDatastore[ii][0]))
                                                        theColumnValues.append(theValue)
                                                except:

                                                    pass

                            xtimeCol[col]         = xtimeForOneCol
                            columnDataToPlot[col] = theColumnValues
                            countTimeBinsMax=max(countTimeBinsMax, countTimeBins)
                            countTimeBinsWithDataMax=max(countTimeBinsWithDataMax, countTimeBinsWithData)



        ########
        for nn in xtimeCol:
            anyData=max(anyData,len(nn))
        sendToLog("type: "+str(tType)+", now graphing # of datapoints: "+str(anyData) + "; #ofBins "+str(countTimeBinsMax)+ "; Ymin/max L: "+str(yMinL)+" "+str(yMaxL)+" ..R: "+str(yMinR)+" "+str(yMaxR),level=1 )
    except  Exception, e:
                sendToLog("Line '%s' has error='%s'" % (sys.exc_traceback.tb_lineno, e),1)
    return anyData



def getminMaxPerTimeperiod(minMax,timePeriod,xtimeForOneCol,theColumnValues,weight):
    global eventData, eventIndex, DEVICE, dataColumnToDevice0Prop1Index

    try:
        Y=-1*minMax*99999999999999999
        X=0
        W=1
        xvals=[]
        yvals=[]
        wvals=[]
        doW = len(weight) >0
        dTime=-1
        #sendToLog("getminMaxPerTimeperiod " +str(minMax)+"  "+ str(timePeriod) +"  "+ str(len(xtimeForOneCol)) )# +" "+ str(xtimeForOneCol)+"  " +str(theColumnValues))
        #if timePeriod.find("m") >-1: 
        #     sendToLog("getminMaxPerTimeperiod  data "+ str(xtimeForOneCol)+"  " +str(theColumnValues))
        new = True
        for mm in range(len(xtimeForOneCol)):
            if timePeriod !="" and  dTime !=  xtimeForOneCol[mm].strftime(timePeriod):
                if dTime != -1:
                    xvals.append(X)
                    yvals.append(Y)
                    if doW:
                        wvals.append(W)
                Y=-1*minMax*99999999999999999
                X=0
                W=1
                dTime= xtimeForOneCol[mm].strftime(timePeriod)
                #sendToLog("getminMaxPerTimeperiod  dTime " +str(dTime) )
                new = False
            if (minMax > 0 and Y < theColumnValues[mm] ) or  (minMax < 0 and Y > theColumnValues[mm] ):   
                X = xtimeForOneCol[mm]
                Y = theColumnValues[mm]
                if doW: W = weight[mm] 
                new= True
                
        if  timePeriod !="" and new:
            xvals.append(X)
            yvals.append(Y)
            if doW:
                wvals.append(W)
                           
        #sendToLog("getminMaxPerTimeperiod  return " +str(xvals)+"  "+ str(yvals) +"  "+ str(wvals) )
        if timePeriod != "": return xvals, yvals, weight
        else:                return [X], [Y], [W]

    except  Exception, e:
        sendToLog("Line '%s' has error='%s'" % (sys.exc_traceback.tb_lineno, e),1)
    return [],[],[]


def do_DisplayData( plotN, filenamesToPlot, XisDate, tType,colOffset, BorderColor):
    global PLOT,oldPLOT, NOTdataFromTimeSeries
    global newData, plotDatastore, weightDataToPlot
    global numberOfPlots,  noOfDays, numberOfMinutesInTimeBins, numberOfTimeTypes, numberOfTimeBins, dataColumnCount
    global indigoPlotDataDir, parameterFile, indigoPNGdir,indigoPath
    global myPID, msgCount, logHandle, quitNOW
    global plotSizeNames, plotTimeNames, timeDataNumbers, dataVersion, parameterVersion,debugEnable
    global xtimeCol, columnDataToPlot,  countTimeBinsMax, countTimeBinsWithDataMax, zeroYColumn
    global yMinL, yMinR, yMaxR, yMaxL, xMax, xMin, y1, y2, firstDaytoPlot, lastDaytoPlot, lastBinTime, colsToPlot, colsToPlotB,columnsToPlot, numberofNonTimeBins 
    global noOfMinutesInTimeBins, emptyBlanks, MHD, d0, d1, doPLOT, zeroYValue,  BordOff, Xfline1, Xfline2, xTime, DeviceNamePlotpng0
    global eventData, eventIndex, DEVICE, dataColumnToDevice0Prop1Index

    try:

# def prep_Display(plotN, countTimeBinsMax        
        if len(str(plotN["resxy"][0])) >6 and len(str(plotN["resxy"][1])) >6:
            textScale = float(plotN["Textscale21"])
        else:
            textScale = 1.
        mlp.rcParams["legend.fontsize"]	= "small"
        mlp.rcParams["legend.frameon"]	= False
        mlp.rcParams["xtick.labelsize"]	= "small"
        mlp.rcParams["ytick.labelsize"]	= "small"
        mlp.rcParams["font.family"]		= plotN["TextMATFont"]

        try:
            mlp.rcParams["text.color"]		= plotN["TextColor"]
            mlp.rcParams["xtick.color"]		= plotN["TextColor"]
            mlp.rcParams["ytick.color"]		= plotN["TextColor"]
        except:
            sendToLog(" error with textColor parameters " +str(plotN["TextColor"]),0)


        for ss in range(0,2):									# this is for s1 / s2 size names
            DeviceNamePlotpng= DeviceNamePlotpng0+"-"+plotSizeNames[ss]+".png"

            if len(str(plotN["resxy"][ss])) < 6: continue			# no proper size given skip this plot
            if ss == 1:
                textSize = float(int(float(plotN["TextSize"] ) *textScale))
            else:
                textSize = float(plotN["TextSize"] )

        ### setup plots
            try:
                mlp.rcParams["font.size"]		= textSize
            except:
                sendToLog(" error with textSize parameters "+str(plotN["TextSize"]) ,0)



            if tType==0:
                if  plotN["PlotType"] == "dataFromTimeSeries": 	mlp.rcParams["xtick.major.pad"]	= 12 *(max(1.,textSize/12.))
                elif XisDate and  Xfline2!="" and  countTimeBinsMax < 370:
                                                                mlp.rcParams["xtick.major.pad"]	= 12 *(max(1.,textSize/12.))
                else:											mlp.rcParams["xtick.major.pad"]	= 5 *(max(1.,textSize/12.))

            if tType==1:
                if countTimeBinsMax > 24*9:	mlp.rcParams["xtick.major.pad"]	= 12 *(max(1.,textSize/12.))
                else:						mlp.rcParams["xtick.major.pad"]	= 12 *(max(1.,textSize/12.))
            if tType==2:
                if countTimeBinsMax < 241:		mlp.rcParams["xtick.major.pad"]	= 12 *(max(1.,textSize/12.))
                else:						mlp.rcParams["xtick.major.pad"]	= 5 *(max(1.,textSize/12.))

            try:
                xres =(float(plotN["resxy"][ss].split(",")[0])/100.)
                yres =(float(plotN["resxy"][ss].split(",")[1])/100.)
            except:
                xres = 8
                yres = 4


            if plotN["XYvPolar"] =="xy":
                do_xyPlot(plotN, xres,yres, DeviceNamePlotpng, xMax,xMin, textSize,BordOff,BorderColor,firstDaytoPlot,lastDaytoPlot,y1,y2,tType,XisDate)
            else:   # polar
                do_polar(plotN, xres,yres,  DeviceNamePlotpng, xMax,xMin, tType)

        
    except  Exception, e:
                sendToLog("Line '%s' has error='%s'" % (sys.exc_traceback.tb_lineno, e),1)
   #### end do plot              



def  do_xyPlot(plotN, xres,yres, DeviceNamePlotpng, xMax,xMin, textSize,BordOff,BorderColor,firstDaytoPlot,lastDaytoPlot,y1,y2,tType,XisDate):
    global MHD, xtimeCol, colsToPlot, columnDataToPlot,weightDataToPlot, zeroYColumn,xTime, emptyBlanks
    global eventData, eventIndex, DEVICE, dataColumnToDevice0Prop1Index
                        
                        
    try:
        fig = plt.figure(facecolor=plotN["Background"],figsize=(xres,yres),dpi=100)
        # us this to move box up:  
        if textSize> 12.: fig.subplots_adjust(   bottom=(  0.10+0.04*max(1,textSize/12.)*4./yres  )  )

        if  str(plotN["TransparentBackground"]) == "0.0":
            fig.patch.set_alpha(0.0)
            ax = fig.add_subplot(111)
            ax.patch.set_alpha(1.0)
        else:
            fig.patch.set_alpha(1.0)
            ax = fig.add_subplot(111, axisbg=plotN["Background"])
        if textSize> 12.: delYTitle=  1.+0.02*max(1,textSize/12.)*4./yres   
        else : delYTitle=1.
        
        fig.suptitle(plotN["TitleText"],y=0.95* delYTitle)
        if len(plotN["ExtraText"]) >0:
            if plotN["ExtraTextFrontBack"] == "back": alphaText=0.5
            else:alphaText=1.0
            fig.text(
                 plotN["ExtraTextXPos"]
                ,plotN["ExtraTextYPos"]
                ,plotN["ExtraText"]
                ,rotation=plotN["ExtraTextRotate"]
                ,color=plotN["ExtraTextColorRGB"]
                ,size=plotN["ExtraTextSize"]
                ,alpha=alphaText)
        ax.spines["top"].set_color(plotN["TextColor"])
        ax.spines["bottom"].set_color(plotN["TextColor"])
        ax.spines["left"].set_color(plotN["TextColor"])
        ax.spines["right"].set_color(plotN["TextColor"])

        # y axis

        ax.set_ylabel(plotN["LeftLabel"],color=plotN["TextColor"])
        Yformat = True
        if plotN["LeftLog"] =="1" or plotN["LeftLog"].upper() =="LOG":
            ax.set_yscale('log')
        if len(plotN["LeftScaleRange"]) > 2:
            yRange= plotN["LeftScaleRange"].split(":")
            ax.set_ylim( float(yRange[0]), float(yRange[1]) )
        if len(plotN["LeftScaleTics"]) >2 and (plotN["LeftScaleTics"]).count(",") > 0  and y1 :
            theList= plotN["LeftScaleTics"].split(",")
            numtics = len(theList)
            tickNum =[]
            tickText=[]
            tn =1.
            tx = str(tn)
            for nT in range(numtics):
                if   theList[nT].count('"') ==2:
                    try:
                        Yformat = False
                        dd,tx,tn = theList[nT].split('"')
                        tn = float(tn.strip(" "))
                    except:
                        sendToLog(" bad Yleft format string: "+ plotN["RightScaleTics"],level=1)
                        tn = 0
                        tx = "bad format string"
                elif theList[nT].count('"') ==0:
                    try:
                        tn = float(theList[nT].strip(" "))
                        tx=str(tn)
                    except:
                        sendToLog(" bad Yleft format string: "+ plotN["RightScaleTics"],level=1)
                        tn = 0
                        tx = "bad format string"
                else:
                    tn = tn
                    tx = tx



                tickNum.append(tn)
                tickText.append(tx)
            ax.set_yticks(tickNum)
            ax.set_yticklabels(tickText)
        elif BordOff[1] =="0":
            ax.set_yticklabels(emptyBlanks,color =BorderColor[1])

        # grids
        if plotN["Grid"] !="0" and plotN["Grid"].find("y2")==-1:
            if plotN["Grid"].find("-") ==-1:
                    ax.set_axisbelow(True)
                    zorder=-1
            else:
                    ax.set_axisbelow(False)
                    zorder=99


            ls=":" ; lw=0.5
            if	 plotN["Grid"].find("1")>-1 : ls=":" ; lw=0.5
            elif plotN["Grid"].find("3")>-1 : ls="-" ; lw=1
            else:							  ls="-" ; lw=0.5

            if plotN["Grid"].find("-") ==-1:
                ax.set_axisbelow(True)
                zorder=-99
            else:
                ax.set_axisbelow(False)
                zorder=+99


            if plotN["Grid"].find("onlyx")==-1:
                ax.yaxis.grid(True,zorder=zorder, which="major", linestyle=ls,linewidth= lw, color=plotN["TextColor"])

            if plotN["Grid"].find("onlyy")==-1:
                ax.xaxis.grid(True,zorder=zorder, which="major", linestyle=ls,linewidth= lw, color=plotN["TextColor"])
                if not XisDate:
                    if tType==0:
                        ax.xaxis.grid(True,zorder=zorder, which="minor", linestyle=':',linewidth= lw, color=plotN["TextColor"])
                    elif tType==1 and  numberOfTimeBins[1] > 24*7:
                        ax.xaxis.grid(True,zorder=zorder, which="minor", linestyle=':',linewidth= lw, color=plotN["TextColor"])
                    elif tType==2 and  numberOfTimeBins[2] < 121:
                        ax.xaxis.grid(True,zorder=zorder, which="minor", linestyle=':',linewidth= lw, color=plotN["TextColor"])
        else:
            ax.grid(False)#, which="major", linestyle=" ",linewidth= 0,color=plotN["Background"] )
        try:
            if int(plotN["LeftScaleDecPoints"]) >=0  and Yformat:
                if not(plotN["LeftLog"] == "1" or plotN["LeftLog"].upper() =="LOG"):	ax.yaxis.set_major_formatter(FormatStrFormatter("%."+plotN["LeftScaleDecPoints"]+"f"))
                else:																	ax.yaxis.set_major_formatter(mlp.ticker.FormatStrFormatter("%."+plotN["LeftScaleDecPoints"]+"f"))
        except:
            pass


        # y2 axis
        if  y2 or len(plotN["RightScaleTics"]) >0 or len(plotN["RightScaleRange"]) > 2:
            ax2 = ax.twinx()
            ax.set_zorder(ax2.get_zorder()+1) # put ax in front of ax2
            ax.patch.set_visible(False) # hide the 'canvas'
            Yformat = True
            ax2.set_ylabel(plotN["RightLabel"], color=plotN["TextColor"], alpha=1.0)

            #for ll in ax2.yaxis.get_ticklabels():
            #	ll.set_color( color =BorderColor[3])
            #for ll in ax2.yaxis.get_ticklines():
            #	ll.set_color( color =BorderColor[3])
            if plotN["RightLog"] =="1" or plotN["RightLog"].upper() =="LOG":
                ax2.set_yscale('log')
            if len(plotN["RightScaleTics"]) >0 :
                theList= plotN["RightScaleTics"].split(",")
                numtics = len(theList)
                tickNum =[]
                tickText=[]
                tn =1.
                tx = str(tn)
                for nT in range(numtics):
                    if   theList[nT].count('"') ==2:
                        try:
                            Yformat = False
                            dd,tx,tn = theList[nT].split('"')
                            tn = float(tn.strip(" "))
                        except:
                            sendToLog(" bad Yright format string: "+ plotN["RightScaleTics"],level=1)
                            tn = 0
                            tx = "bad format string"
                    elif theList[nT].count('"') ==0:
                        try:
                            tn = float(theList[nT].strip(" "))
                            tx=str(tn)
                        except:
                            sendToLog(" bad Yright format string: "+ plotN["RightScaleTics"],level=1)
                            tn = 0
                            tx = "bad format string"
                    else:
                        tn = tn
                        tx = tx
        
                    tickNum.append(tn)
                    tickText.append(tx)
                ax2.set_yticks(tickNum)
                ax2.set_yticklabels(tickText, color= BorderColor[3],alpha=1.0)
            elif BordOff[3] =="0":
                ax2.set_yticklabels(emptyBlanks,color =BorderColor[3])


            if plotN["Grid"] !="0" and plotN["Grid"].find("y2")>-1:
                if	 plotN["Grid"].find("1")>-1 : ls=":" ; lw=0.5
                elif plotN["Grid"].find("3")>-1 : ls="-" ; lw=1
                else:							  ls="-" ; lw=0.5

                if plotN["Grid"].find("-") ==-1:
                    ax2.set_axisbelow(True)
                    ax.set_axisbelow(True)
                    zorder=-99
                else:
                    ax2.set_axisbelow(False)
                    ax.set_axisbelow(False)
                    zorder=99

                ls=":" ; lw=0.5
                if	 plotN["Grid"].find("1")>-1 : ls=":" ; lw=0.5
                elif plotN["Grid"].find("3")>-1 : ls="-" ; lw=1
                else:							  ls="-" ; lw=0.5



                if plotN["Grid"].find("-") ==-1:
                    ax2.set_axisbelow(False)
                    ax.set_axisbelow(False)
                else:
                    ax2.set_axisbelow(True)
                    ax.set_axisbelow(True)

                if plotN["Grid"].find("onlyx")==-1:
                    ax2.yaxis.grid(True,zorder=zorder, which="major", linestyle=ls,linewidth= lw, color=plotN["TextColor"])

                if plotN["Grid"].find("onlyy")==-1:
                    ax.xaxis.grid(True,zorder=zorder, which="major", linestyle=ls,linewidth= lw, color=plotN["TextColor"])
                    if tType==0:
                        ax.xaxis.grid(True,zorder=zorder, which="minor", linestyle=':',linewidth= lw, color=plotN["TextColor"])
                    elif tType==1 and  numberOfTimeBins[1] > 24*7:
                        ax.xaxis.grid(True,zorder=zorder, which="minor", linestyle=':',linewidth= lw, color=plotN["TextColor"])
                    elif tType==2 and  numberOfTimeBins[2] < 121:
                        ax.xaxis.grid(True,zorder=zorder, which="minor", linestyle=':',linewidth= lw, color=plotN["TextColor"])

        
            else:
                ax2.grid(False)#, which="major", linestyle=" ",linewidth= 0,color=plotN["Background"] )

        try:
            if int(plotN["RightScaleDecPoints"]) >=0 and y2 and Yformat :
                if not(plotN["RightLog"] == "1" or plotN["RightLog"].upper() =="LOG"):	ax2.yaxis.set_major_formatter(FormatStrFormatter("%."+plotN["RightScaleDecPoints"]+"f"))
                else:																	ax2.yaxis.set_major_formatter(mlp.ticker.FormatStrFormatter("%."+plotN["RightScaleDecPoints"]+"f"))
        except:
            pass
        try:
            if len(plotN["RightScaleRange"]) > 2:
                yRange= plotN["RightScaleRange"].split(":")
                ax2.set_ylim( float(yRange[0]), float(yRange[1]) )
        except:
            pass
            
            
        # plot lines
        if  plotN["PlotType"] == "dataFromTimeSeries":
            ax.xaxis_date()

        ax.set_xlim(firstDaytoPlot,lastDaytoPlot)
        if str(plotN["drawZeroLine"]).upper() =="TRUE": # plot "zero line for sparse data it is invisible, to make sure that all x axis is shown.
            ax.plot( xTime,zeroYColumn,ls="", color=plotN["Background"],lw=1, label="", alpha=1.0)
        sendToLog("line#; width;  color; Transp;   R/L;  Func; shift;       type;       smooth;      C-offset;              Nformat;EveryRepeat;   key------",level=1)
        for ll0 in range(colsToPlot):
            zorder = ll0 - 10
            try:
                ll =         columnsToPlot[ll0][1]
                lF =         plotN["lines"][ll]["lineFunc"]
                lc =         plotN["lines"][ll]["lineColor"]
                lt =         plotN["lines"][ll]["lineType"]
                lw =  float( plotN["lines"][ll]["lineWidth"])
                lw2= lw/2
            except  Exception, e:
                sendToLog("Line '%s' has error='%s'" % (sys.exc_traceback.tb_lineno, e),level=1)
                sendToLog("colsToPlot "+ str(colsToPlot) +"  llo " +str(ll0)+" columnsToPlot "+str(columnsToPlot),level=1)
                continue
            if columnsToPlot[ll0][0] > 0:
                lk =         plotN["lines"][ll]["lineKey"]
            else:
                lk = ""
            lr =         plotN["lines"][ll]["lineLeftRight"]
            sh =         plotN["lines"][ll]["lineShift"]
            la =  float( plotN["TransparentBlocks"])
            sm =         plotN["lines"][ll]["lineSmooth"]
            nO =         plotN["lines"][ll]["lineNumbersOffset"]
            nF =         plotN["lines"][ll]["lineNumbersFormat"]
            nR =         plotN["lines"][ll]["lineEveryRepeat"]
            sendToLog( unicode(ll).rjust(5)+unicode(lw).rjust(7)+ unicode(lc).rjust(8)+ unicode(la).rjust(8)+ unicode(lr).rjust(7)+ unicode(lF).rjust(7)+ unicode(sh).rjust(7)+ unicode(lt).rjust(12)+sm.rjust(14)+nO.rjust(15)+nF.rjust(23)+nR.rjust(11)+";  "+unicode(lk),level=1)

            if ll0 > len(xtimeCol)-1:  # this should not happen
                sendToLog( u"no x data(1) for line " +str(ll0+1)+"  # of xcolumns:"+ str(len(xtimeCol)),level=1)
                continue
            if len(xtimeCol[ll0])< 1:
                sendToLog( u"no x data(2) for line " +str(ll0+1),level=1)
                continue # skip empty lines

            ######### right axis lines
            if lr == "Right" and y2:
                if lF=="C":  # colorbar
                    cb= ax2.scatter(xtimeCol[ll0],columnDataToPlot[ll0],c=weightDataToPlot[ll0],edgecolor="none",lw=lw, label=lk)
                    if plotN["RightLabel"] !="":
                        position=fig.add_axes([0.93,0.2,0.02,0.6])
                        cbT = fig.colorbar(cb,cax=position )
                    else:
                        position=fig.add_axes([0.92,0.2,0.02,0.6])
                        cbT = fig.colorbar(cb,cax=position )
                        cbT.set_label(plotN["RightLabel"], color =plotN["TextColor"])
                elif lF=="S": # solid dots
                    ax2.scatter(xtimeCol[ll0],columnDataToPlot[ll0],s=weightDataToPlot[ll0],color=lc,edgecolor=lc, label=lk)
                elif lF=="E":  # empty dots
                    ax2.scatter(xtimeCol[ll0],columnDataToPlot[ll0],s=weightDataToPlot[ll0],color=plotN["Background"],edgecolor=lc ,label=lk)
                elif lt =="LineSolid":	ax2.plot(xtimeCol[ll0],columnDataToPlot[ll0],ls="-",zorder=zorder, color=lc,lw=lw2, label=lk)
                elif lt =="LineDashed":	ax2.plot(xtimeCol[ll0],columnDataToPlot[ll0],ls=":",zorder=zorder, color=lc,lw=lw2, label=lk)

                elif lt =="Impulses":
                    for ii in range(len(xtimeCol[ll0])):
                        if ii==0:
                            ax2.vlines(xtimeCol[ll0][ii],0,columnDataToPlot[ll0][ii],zorder=zorder, color=lc,lw=lw, label=lk)
                        else:
                            ax2.vlines(xtimeCol[ll0][ii],0,columnDataToPlot[ll0][ii],zorder=zorder, color=lc,lw=lw)
                elif lt =="averageLeft":
                    npointToplot=int(max(1,len(xtimeCol[ll0]) *0.08))
                    toPlot   = firstDaytoPlot
                    fromPlot = firstDaytoPlot+ (lastDaytoPlot-firstDaytoPlot)/40
                    average= sum(columnDataToPlot[ll0])/max(1.0,len(xtimeCol[ll0]))
                    ax2.hlines(average, fromPlot, toPlot,zorder=zorder, color=lc,lw=lw2)
                elif lt =="averageRight":
                    average= sum(columnDataToPlot[ll0])/max(1.0,len(xtimeCol[ll0]))
                    toPlot   = lastDaytoPlot
                    fromPlot = lastDaytoPlot- (lastDaytoPlot-firstDaytoPlot)/40
                    ax2.hlines(average, fromPlot, toPlot,zorder=zorder, color=lc,lw=lw2)


                elif lt.find("DOT")==0:	ax2.scatter(xtimeCol[ll0],columnDataToPlot[ll0],marker=lt[3:],zorder=zorder, color=lc,edgecolor=lc,lw=lw2, label=lk)
                elif lt =="FilledCurves":
                    yLimit = ax2.get_ylim()
                    ax2.fill_between(xtimeCol[ll0],columnDataToPlot[ll0],yLimit[0],zorder=zorder,facecolor=lc,color=lc, alpha=la, lw=0.)
                    if len(lk) > 0:
                        ypp= 0.8 - ll0*0.05
                        fig.text(0.81,ypp,r"$\blacksquare $   "+lk,color=lc,size=textSize*0.9)
                        #fig.text(0.81,0.77,r"$\blacksquare $  "+lk,color=lc,size=textSize*0.9)
                elif lt =="Numbers":
                    nOxy= nO.split(",")
                    if lw >0: fontSize= int((lw*2.5+4))
                    for i in range(len(xtimeCol[ll0])):
                        try: 
                            ax2.annotate((nF%columnDataToPlot[ll0][i]), xy=(xtimeCol[ll0][i],columnDataToPlot[ll0][i]), xytext=(int(10*float(nOxy[0])),int(10*float(nOxy[1]))),textcoords='offset points',color=lc, fontsize=fontSize)
                        except:
                            pass
                elif lt.find("Histogram")==0:

                    nbins = len(xtimeCol[ll0])
                    if  plotN["PlotType"] == "dataFromTimeSeries":
                        if tType ==0: wid = 5./60./60.*2.5
                        if tType ==1: wid = 60./60./60.*2.5
                        if tType ==2: wid = 24.*60./60./60.*2.5
                    elif  XisDate:
                            wid = 1
                    else:
                            wid =(xtimeCol[ll0][nbins-1]-xtimeCol[ll0][0])/max(nbins,0.0000000000001)/.8

                    if   lt =="Histogram0"	:
                        ax2.bar(xtimeCol[ll0], columnDataToPlot[ll0],zorder=zorder, width=wid, edgecolor=lc,lw=lw2, label=lk,facecolor='none',fill=False,alpha=la,align='center')
                    else:
                        bars=ax2.bar(xtimeCol[ll0], columnDataToPlot[ll0],zorder=zorder, width=wid, facecolor=lc,lw=lw2, label=lk,alpha=la,align='center')
                        if   lt =="Histogram1":	[bar.set_hatch("x")  for bar in bars]
                        elif lt =="Histogram2":	[bar.set_hatch("*")  for bar in bars]
                        elif lt =="Histogram4":	[bar.set_hatch("\\") for bar in bars]
                        elif lt =="Histogram5":	[bar.set_hatch("/")  for bar in bars]
        
        
            ######### left axis lines
            if lr == "Left" and y1:
                if lF=="C":  # colorbar
                    cb= ax.scatter(xtimeCol[ll0],columnDataToPlot[ll0],c=weightDataToPlot[ll0],edgecolor="face",lw=lw, label=lk)
                    if y2 and plotN["RightLabel"] !="":
                        position=fig.add_axes([0.95,0.2,0.02,0.6])
                        cbT = fig.colorbar(cb,cax=position )
                    elif y2:
                        position=fig.add_axes([0.922,0.2,0.02,0.6])
                        cbT = fig.colorbar(cb,cax=position )
                    elif not y2:
                        position=fig.add_axes([0.91,0.2,0.02,0.6])
                        cbT = fig.colorbar(cb,cax=position )
                        cbT.set_label(plotN["RightLabel"], color =plotN["TextColor"])
                elif lF=="S":  # solid dots
                    ax.scatter(xtimeCol[ll0],columnDataToPlot[ll0],s=weightDataToPlot[ll0],color=lc,edgecolor=lc, label=lk)
                elif lF=="E":  # empty dots
                    ax.scatter(xtimeCol[ll0],columnDataToPlot[ll0],s=weightDataToPlot[ll0],color=plotN["Background"],edgecolor=lc ,label=lk)
                elif lt =="LineSolid":	 ax.plot(xtimeCol[ll0],columnDataToPlot[ll0],ls="-",zorder=zorder, color=lc,lw=lw2, label=lk)

                elif lt =="Impulses":
                    for ii in range(len(xtimeCol[ll0])):
                        if ii==0:
                            ax.vlines(xtimeCol[ll0][ii],0,columnDataToPlot[ll0][ii],zorder=zorder, color=lc,lw=lw, label=lk)
                        else:
                            ax.vlines(xtimeCol[ll0][ii],0,columnDataToPlot[ll0][ii],zorder=zorder, color=lc,lw=lw)

                elif lt =="averageLeft":
                    npointToplot=int(max(1,len(xtimeCol[ll0]) *0.08))
                    average= sum(columnDataToPlot[ll0])/max(1.0,len(xtimeCol[ll0]))
                    fromPlot = firstDaytoPlot
                    toPlot   = firstDaytoPlot+ (lastDaytoPlot-firstDaytoPlot)/40
                    ax.hlines(average, fromPlot, toPlot,zorder=zorder, color=lc,lw=lw2)
                elif lt =="averageRight":
                    nnl=len(xtimeCol[ll0])-1
                    average= sum(columnDataToPlot[ll0])/max(1.0,len(xtimeCol[ll0]))
                    toPlot   = lastDaytoPlot
                    fromPlot = lastDaytoPlot- (lastDaytoPlot-firstDaytoPlot)/40
                    ax.hlines(average, fromPlot, toPlot,zorder=zorder, color=lc,lw=lw2)## lastTime

                elif lt =="LineDashed":	 ax.plot(xtimeCol[ll0],columnDataToPlot[ll0],ls=":",zorder=zorder, color=lc,lw=lw2, label=lk)
                elif lt.find("DOT")==0:	 ax.scatter(xtimeCol[ll0],columnDataToPlot[ll0],marker=lt[3:],zorder=zorder, color=lc,edgecolor=lc,lw=lw2, label=lk)
                elif lt =="FilledCurves":
                    yLimit = ax.get_ylim()
                    ax.fill_between( xtimeCol[ll0], columnDataToPlot[ll0],yLimit[0],zorder=zorder,facecolor=lc,color=lc,edgecolor=lc, alpha=la, lw=0.)
                    if len(lk) > 0:
                        ypp= 0.8 - ll0*0.05
                        fig.text(0.14,ypp,r"$\blacksquare $   "+lk,color=lc,size=textSize*0.9)
                        ##fig.text(0.14,0.77,r"$\blacksquare $   "+lk,color=lc,size=textSize*0.9)
                elif lt =="Numbers":
                    nOxy= nO.split(",")
                    if lw >0: fontSize= int((lw*2.5+4))
                    for i in range(len(xtimeCol[ll0])):
                        try:
                            a=float(columnDataToPlot[ll0][i])
                            ax.annotate((nF%columnDataToPlot[ll0][i]), xy=(xtimeCol[ll0][i],columnDataToPlot[ll0][i]), xytext=(int(10*float(nOxy[0])),int(10*float(nOxy[1]))),textcoords='offset points',color=lc, fontsize=fontSize)
                        except:
                            ax.annotate("%s"%columnDataToPlot[ll0][i], xy=(xtimeCol[ll0][i],0.), xycoords='data',xytext=(0,-10),textcoords='offset points',color=lc, fontsize=fontSize)
                            
                elif lt.find("Histogram")==0:
                    nbins = len(xtimeCol[ll0])
                    if  plotN["PlotType"] == "dataFromTimeSeries" :
                        if tType ==0: wid = 5./60./60.*2.5
                        if tType ==1: wid = 60./60./60.*2.5
                        if tType ==2: wid = 24.*60./60./60.*2.5
                    elif  XisDate:
                                wid = 1
                    else:
                                wid = (xtimeCol[ll0][nbins-1]-xtimeCol[ll0][0])/max(nbins,0.0000000000001)/.8
                    nbins = len(xtimeCol[ll0])
                    if   lt =="Histogram0"	:
                        ax.bar(xtimeCol[ll0], columnDataToPlot[ll0],zorder=zorder, width=wid, edgecolor=lc,lw=lw2, label=lk,facecolor='none',fill=False,alpha=la,align='center')
                    else:
                        bars=ax.bar(xtimeCol[ll0], columnDataToPlot[ll0],zorder=zorder, width=wid, facecolor=lc,lw=lw2, label=lk,alpha=la,align='center')
                        if   lt =="Histogram1":	[bar.set_hatch("x")  for bar in bars]
                        elif lt =="Histogram2":	[bar.set_hatch("*")  for bar in bars]
                        elif lt =="Histogram4":	[bar.set_hatch("\\") for bar in bars]
                        elif lt =="Histogram5":	[bar.set_hatch("/")  for bar in bars]

        # not needed ,seems to work with out due to zorder
        #					if str(plotN["TransparentBackground"]) == "0.0":		plt.savefig(DeviceNamePlotpng,transparent=True,              edgecolor='none')
        #					else:													plt.savefig(DeviceNamePlotpng,facecolor=fig.get_facecolor(), edgecolor='none')
        #						sendToLog("after 2 save: "+str(time.time()-t2),level=1)




        # x axis has to be after other things to make it work properly

        if  plotN["PlotType"] == "dataFromTimeSeries":
            if BordOff[0] =="0":
                ax.set_xticklabels(emptyBlanks,color =BorderColor[3])
            else:
                
                if plotN["MHDFormat"][tType].lower() !="off":
                    try: 
                        ticksDensity = float(plotN["MHDFormat"][tType])
                    except:
                        ticksDensity = 1
                    
                    if tType == 0:
                        if   int(plotN["MHDDays"][0]) ==1:  fraction = 0.125
                        elif int(plotN["MHDDays"][0]) ==2:  fraction = 0.125
                        elif int(plotN["MHDDays"][0]) ==3:  fraction = 0.25
                        elif int(plotN["MHDDays"][0]) ==4:  fraction = 0.25
                        elif int(plotN["MHDDays"][0]) ==5:  fraction = 0.5
                        elif int(plotN["MHDDays"][0]) ==6:  fraction = 0.5
                        elif int(plotN["MHDDays"][0]) ==7:  fraction = 0.5
                        elif int(plotN["MHDDays"][0]) < 15: fraction = 1
                        elif int(plotN["MHDDays"][0]) < 31: fraction = 11
                        else : 							    fraction = 11

                        if fraction < 10:
                            ax.xaxis.set_major_formatter(DateFormatter("%a"))  # weekday
                            ax.xaxis.set_major_locator(DayLocator())
                            minorLocator   = MultipleLocator(fraction/ticksDensity)
                            ax.xaxis.set_minor_locator(minorLocator)
                            if plotN["ampm"] =="24":
                                if fraction >0.25:
                                    ax.xaxis.set_minor_formatter(DateFormatter("%H"))
                                else:
                                    ax.xaxis.set_minor_formatter(DateFormatter("%H:%M"))
                            else:
                                if fraction >0.25:
                                    ax.xaxis.set_minor_formatter(DateFormatter("%l"))
                                else:
                                    ax.xaxis.set_minor_formatter(DateFormatter("%l %p"))
                        else:
                            ax.xaxis.set_major_formatter(DateFormatter("#")) #  a # sign at beginning of week
                            ax.xaxis.set_major_locator(WeekdayLocator(byweekday=0, interval=1, tz=None))  # always do monday for >= 2 weeks
                            ax.xaxis.set_minor_formatter(DateFormatter("%a"))  # weekday 
                            ax.xaxis.set_minor_locator(DayLocator(interval=2, tz=None))

                    if tType == 1:
                        if countTimeBinsMax < 24*10:
                            ax.xaxis.set_major_formatter(DateFormatter("%a"))
                            ax.xaxis.set_major_locator(DayLocator())
                            ax.xaxis.set_minor_locator(HourLocator( interval=int(12/ticksDensity), tz=None))
                            ax.xaxis.set_minor_formatter(DateFormatter("%H"))
                        elif countTimeBinsMax < 24*21 :
                            ax.xaxis.set_major_formatter(DateFormatter("#"))
                            ax.xaxis.set_major_locator(WeekdayLocator(byweekday=0, interval=1, tz=None))
                            ax.xaxis.set_minor_locator(DayLocator())
                            ax.xaxis.set_minor_formatter(DateFormatter("%a"))
                        elif countTimeBinsMax < 24*40:
                            ax.xaxis.set_major_formatter(DateFormatter("#"))
                            ax.xaxis.set_major_locator(WeekdayLocator(byweekday=0, interval=1, tz=None))  # always do monday for >= 2 weeks
                            ax.xaxis.set_minor_formatter(DateFormatter("%a"))
                            ax.xaxis.set_minor_locator(DayLocator(interval=int(2/ticksDensity), tz=None))
                        elif countTimeBinsMax < 24*60:
                            ax.xaxis.set_major_formatter(DateFormatter("%b"))
                            ax.xaxis.set_major_locator(MonthLocator())
                            ax.xaxis.set_minor_formatter(DateFormatter("%a"))
                            ax.xaxis.set_minor_locator(DayLocator(interval=int(4/ticksDensity), tz=None))
                        else:
                            ax.xaxis.set_major_formatter(DateFormatter("%b"))
                            ax.xaxis.set_major_locator(MonthLocator())
                            ax.xaxis.set_minor_formatter(DateFormatter("%a"))
                            ax.xaxis.set_minor_locator(DayLocator(interval=int(4/ticksDensity), tz=None))

                    if tType == 2:
                        if countTimeBinsMax < 121 :
                            ax.xaxis.set_major_formatter(DateFormatter("%b"))
                            ax.xaxis.set_major_locator(MonthLocator())
                            ax.xaxis.set_minor_locator(WeekdayLocator(byweekday=0, interval=int(1/ticksDensity), tz=None))
                            ax.xaxis.set_minor_formatter(DateFormatter("%a-%d"))
                        elif countTimeBinsMax < 241 :
                            ax.xaxis.set_major_formatter(DateFormatter("%b")) # month short 
                            ax.xaxis.set_major_locator(MonthLocator())
                            ax.xaxis.set_minor_locator(WeekdayLocator(byweekday=0, interval=int(1/ticksDensity), tz=None))
                            ax.xaxis.set_minor_formatter(DateFormatter("%d"))
                        elif countTimeBinsMax < 390 :
                            ax.xaxis.set_major_formatter(DateFormatter("%b"))
                            ax.xaxis.set_major_locator(MonthLocator())
                        else:
                            pass  #  leave it to MATPLOT

        else:
            XaxisON = True
            ax.set_xlabel(plotN["XLabel"], color =plotN["TextColor"], alpha=1.0)
            if XisDate:
                if BordOff[0] =="0":
                    ax.set_xticklabels(emptyBlanks,color =BorderColor[0])
                else:
                    #sendToLog(Xformat+"  "+str(Xformat.find("\\n")),level=1)
                    #sendToLog(str(Xfline1)+"-"+str(Xfline2)+"-",level=1)
                    ax.xaxis.set_major_formatter(DateFormatter(Xfline1))
                    ax.xaxis.set_major_locator(MonthLocator())

                    if Xfline2!="" :
                        if countTimeBinsMax < 100:
                            ax.xaxis.set_minor_locator(DayLocator( interval=5, tz=None))
                        elif countTimeBinsMax < 200:
                            ax.xaxis.set_minor_locator(DayLocator( interval=10, tz=None))
                        elif countTimeBinsMax < 370:
                            ax.xaxis.set_minor_locator(DayLocator( interval=15, tz=None))
                        else:
                            pass
                        ax.xaxis.set_minor_formatter(DateFormatter(Xfline2))
            else:
                if  plotN["XLog"] =="1" or plotN["XLog"].upper() =="LOG": 			ax.set_xscale('log')
                if BordOff[0] =="0":
                    ax.set_xticklabels(emptyBlanks,color =BorderColor[0])
                else:
                    if plotN["XScaleFormat"] == "none":
                        ax.set_xticklabels([])
                    else:    
                        if len(plotN["XScaleTics"]) >2 and (plotN["XScaleTics"]).count(",") >0 :
                            theList= plotN["XScaleTics"].split(",")
                            numtics = len(theList)
                            tickNum =[]
                            tickText=[]
                            tn =1.
                            tx = str(tn)
                            for nT in range(numtics):
                                if   theList[nT].count('"') ==2:
                                    XaxisON = False
                                    dd,tx,tn = theList[nT].split('"')
                                    tn = float(tn.strip(" "))
                                elif theList[nT].count('"') ==0:
                                    tn = float(theList[nT].strip(" "))
                                    tx=str(tn)
                                else:
                                    tn = tn
                                    tx = tx
            
                                tickNum.append(tn)
                                tickText.append(tx)
                            ax.set_xticks(tickNum)
                            ax.set_xticklabels(tickText, color=BorderColor[0],alpha=1.0)
                        try:
                            if XaxisON:
                                if len(plotN["XScaleFormat"]) >2 :ax.xaxis.set_major_formatter(FormatStrFormatter(plotN["XScaleFormat"]))
                                else:
                                    if int(plotN["XScaleDecPoints"]) >=0 :
                                        if not(plotN["XLog"] == "1" or plotN["XLog"].upper() =="LOG"):	ax.xaxis.set_major_formatter(FormatStrFormatter("%."+plotN["XScaleDecPoints"]+"f"))
                                        else:															ax.xaxis.set_major_formatter(mlp.ticker.FormatStrFormatter("%."+plotN["XScaleDecPoints"]+"f"))
                        except:
                            pass
                    if len(plotN["XScaleRange"]) > 3 and y2:
                        ax.set_xlim(float(plotN["XScaleRange"].split(":")[0]),float(plotN["XScaleRange"].split(":")[1]))




            #	for ll in ax.xaxis.get_ticklabels():
            #		ll.set_color(BorderColor[0])

            #	for ll in ax.yaxis.get_ticklabels():
            #		ll.set_color(BorderColor[1])


        ax.legend(loc= "upper left", ncol=3)
        if y2:
            ax2.legend(loc="upper right", ncol=3 )
        if y2:
            ax.set_zorder(ax2.get_zorder()+1) # put ax in front of ax2
            ax.patch.set_visible(False) # hide the 'canvas'

        if y2:
            set_border(BordOff, ax, ax2=ax2)
        else:    
            set_border(BordOff, ax)
        
        if len(plotN["Raw"]) > 5:
            try:
                sendToLog("executing RAW command: "+plotN["Raw"],level=1)
                exec(plotN["Raw"])
            except:
                sendToLog("..... failed: "+plotN["Raw"],level=1)

        save_plot(DeviceNamePlotpng, fig, plt, plotN["TransparentBackground"], plotN["compressPNGfile"]) 
        sendToLog("Done for "+MHD[tType]+" plot,  .. releasing memory .. cleanup.. ",level=1)

        # CLEAN UP
        try:
            fig.clf()
            plt.close(fig)
            if y1: del ax
            if y2: del ax2
        except:
            pass



    except  Exception, e:
                sendToLog("Line '%s' has error='%s'" % (sys.exc_traceback.tb_lineno, e),1)
    return

 

def do_polar(plotN, xres,yres, DeviceNamePlotpng, xMax,xMin,tType):
    global eventData, eventIndex, DEVICE, dataColumnToDevice0Prop1Index
    global MHD, xtimeCol, colsToPlot, columnDataToPlot
    try:
        y1=True
        fig = plt.figure(facecolor=plotN["Background"],figsize=(xres,yres),dpi=100)
        fig.suptitle(plotN["TitleText"],y=0.98)
        if len(plotN["ExtraText"]) >0:
            if plotN["ExtraTextFrontBack"] == "back": alpaText=0.5
            else:alpaText=1.0
            fig.text(
                 plotN["ExtraTextXPos"]
                ,plotN["ExtraTextYPos"]
                ,plotN["ExtraText"]
                ,rotation=plotN["ExtraTextRotate"]
                ,color=plotN["ExtraTextColorRGB"]
                ,size=plotN["ExtraTextSize"]
                ,alpha=alphaText)

        if  str(plotN["TransparentBackground"]) == "0.0":
            fig.patch.set_alpha(0.0)
            ax = fig.add_subplot(111, polar=True)
            ax.patch.set_alpha(1.0)
        else:
            fig.patch.set_alpha(1.0)
            ax = fig.add_subplot(111, axisbg=plotN["Background"], polar=True)

        for ll0 in range(colsToPlot):
            if len(xtimeCol[ll0])< 1: continue # skip empty lines

            ll =         columnsToPlot[ll0][1]
            lc =         plotN["lines"][ll]["lineColor"]
            lt =         plotN["lines"][ll]["lineType"]
            lw2=  float( plotN["lines"][ll]["lineWidth"])/2.
            lk =         plotN["lines"][ll]["lineKey"]


            if   lt =="LineSolid":	ax.plot(xtimeCol[ll0],columnDataToPlot[ll0],ls="-", color=lc,lw=lw2, label=lk)
            elif lt =="LineDashed":	ax.plot(xtimeCol[ll0],columnDataToPlot[ll0],ls=":", color=lc,lw=lw2, label=lk)
            elif lt.find("DOT")==0:	ax.plot(xtimeCol[ll0],columnDataToPlot[ll0],lt[3:], color=lc,lw=lw2, label=lk)


        if plotN["XLog"] =="log": ax.set_rscale('log')
        if xMax != 999999999999999999.: ax.set_rmax(xMax)
        if xMin != -999999999999999999.: ax.set_rmin(xMin)

        if len(plotN["XScaleTics"]) >2 and (plotN["XScaleTics"]).count(",") > 0  :
            theList= plotN["XScaleTics"].split(",")
            numtics = len(theList)
            tickNum =[]
            tickText=[]
            tn =1.
            tx = str(tn)
            for nT in range(numtics):
                if   theList[nT].count('"') ==2:
                    dd,tx,tn = theList[nT].split('"')
                    tn = float(tn.strip(" "))
                elif theList[nT].count('"') ==0:
                    tn = float(theList[nT].strip(" "))
                    tx=str(tn)
                else:
                    tn = tn
                    tx = tx
                tickNum.append(tn)
                tickText.append(tx)
            ax.set_yticks(tickNum)
            ax.set_yticklabels(tickText)

        xx = plotN["LeftLabel"].split(",")

        Dlabel =["90","60","30","0","330","300","270","240","210","180","150","120"]
        if len(xx)==4:
            Dlabel[0]  = xx[1].encode('utf8')
            Dlabel[1]  = "60"
            Dlabel[2]  = "30"
            Dlabel[3]  = xx[0].encode('utf8')
            Dlabel[4]  = "330"
            Dlabel[5]  = "300"
            Dlabel[6]  = xx[3].encode('utf8')
            Dlabel[7]  = "240"
            Dlabel[8]  = "210"
            Dlabel[9]  = xx[2].encode('utf8')
            Dlabel[10] = "150"
            Dlabel[11] = "120"

        elif  len(xx)==12:
            Dlabel[0]  = xx[3].encode('utf8')
            Dlabel[1]  = xx[2].encode('utf8')
            Dlabel[2]  = xx[1].encode('utf8')
            Dlabel[3]  = xx[0].encode('utf8')
            Dlabel[4]  = xx[11].encode('utf8')
            Dlabel[5]  = xx[10].encode('utf8')
            Dlabel[6]  = xx[9].encode('utf8')
            Dlabel[7]  = xx[8].encode('utf8')
            Dlabel[8]  = xx[7].encode('utf8')
            Dlabel[9]  = xx[6].encode('utf8')
            Dlabel[10] = xx[5].encode('utf8')
            Dlabel[11] = xx[4].encode('utf8')


        tickNum =[x*3.141/180. for x in range(0,360,30)]
        ax.set_xticks(tickNum)
        ax.set_xticklabels(Dlabel, color=plotN["TextColor"],alpha=1.0)
        ax.spines['polar'].set_color(plotN["TextColor"])

        if plotN["Grid"] !="0":
            if	 plotN["Grid"] =="-1":  ls=":" ; lw=1
            elif plotN["Grid"] =="-2":  ls="-" ; lw=1
            elif plotN["Grid"] =="-3":  ls="-" ; lw=2
            elif plotN["Grid"] =="1": ls=":" ; lw=1
            elif plotN["Grid"] =="2": ls="-" ; lw=1
            elif plotN["Grid"] =="3": ls="-" ; lw=2
            ax.grid(True, which="major", linestyle=ls,linewidth= lw, color=plotN["TextColor"])
            if plotN["Grid"].find("-") ==-1: ax.set_axisbelow(True)
        else:
            ax.grid(False)
            if len(plotN["XScaleTics"])<3:
                ax.set_yticks([])
                ax.set_yticklabels([""])
                ax.spines['polar'].set_color(plotN["Background"])

        ax.legend(loc= "upper right")
        ax.set_xlabel(plotN["XLabel"], color =plotN["TextColor"], alpha=1.0)
        lOffset = max(0,len(plotN["XLabel"])-5)*(0.004*float(plotN["TextSize"])/10.*float(plotN["Textscale21"]))
        ax.xaxis.set_label_coords(1.05-lOffset,0.72)

        save_plot(DeviceNamePlotpng, fig, plt, plotN["TransparentBackground"], plotN["compressPNGfile"])
        sendToLog("Done for "+MHD[tType]+" plot,  .. releasing memory .. cleanup.. ",level=1)

        # CLEAN UP
        try:
            fig.clf()
            plt.close(fig)
            if y1: del ax
            if y2: del ax2
        except:
            pass




    except  Exception, e:
                sendToLog("Line '%s' has error='%s'" % (sys.exc_traceback.tb_lineno, e),1)
    return


def set_border(BordOff, ax, ax2=""):
    try:
        if BordOff[0] =="0":
            ax.tick_params( axis="x", which="both", bottom="off", top="off")
            ax.spines["bottom"].set_visible(False)
        if BordOff[1] =="0":
            ax.tick_params( axis="y", which="both", left="off")
            ax.spines["left"].set_visible(False)
        if BordOff[2] =="0":
            ax.tick_params( axis="x", which="both" , top="off")
            ax.spines["top"].set_visible(False)
        if BordOff[3] =="0":
            ax.tick_params( axis="y", which="both", right="off")
            ax.spines["right"].set_visible(False)
        if ax2 != "":    
            if BordOff[0] =="0":
                ax2.tick_params( axis="x", which="both", bottom="off", top="off")
                ax2.spines["bottom"].set_visible(False)
            if BordOff[1] =="0":
                ax2.tick_params( axis="y", which="both", left="off")
                ax2.spines["left"].set_visible(False)
            if BordOff[2] =="0":
                ax2.tick_params( axis="x", which="both" , top="off")
                ax2.spines["top"].set_visible(False)
            if BordOff[3] =="0":
                ax2.tick_params( axis="y", which="both", right="off")
                ax2.spines["right"].set_visible(False)
    except  Exception, e:
        sendToLog("Line '%s' has error='%s'" % (sys.exc_traceback.tb_lineno, e),1)




def save_plot(DeviceNamePlotpng, fig, plt, TransparentBackground, compressPNGfile):

    #### create / save  PLOT 
    try:
        sendToLog("Saving.." ,level=1)
        if str(TransparentBackground) == "0.0":		plt.savefig(DeviceNamePlotpng,transparent=True,              edgecolor='none')  # creates file with .png
        else:										plt.savefig(DeviceNamePlotpng,facecolor=fig.get_facecolor(), edgecolor='none')  # creates file with .png not transparent

        if compressPNGfile:
            cmd = "'"+indigoPath+"Plugins/INDIGOplotD.indigoPlugin/Contents/Server Plugin/pngquant' --force --ext .xxx '"+DeviceNamePlotpng+"'"
            ppp = subprocess.Popen(cmd.encode('utf8'),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()  ## creates a file with .xxx

            if os.path.isfile((DeviceNamePlotpng).encode('utf8')): os.remove((DeviceNamePlotpng).encode('utf8'))
            if os.path.isfile((DeviceNamePlotpng.strip(".png")+".xxx").encode('utf8')):
                os.rename((DeviceNamePlotpng.strip(".png")+".xxx").encode('utf8'),(DeviceNamePlotpng).encode('utf8') )


    except  Exception, e:
        sendToLog("Line '%s' has error='%s'" % (sys.exc_traceback.tb_lineno, e),1)
        sendToLog("savefig error some parameters are wrong for " +DeviceNamePlotpng,level=1)




def dump_garbage():
    gc.collect()
    for x in gc.garbage:
        s = str(x)
        if len(s)<2: return
        if len(s) > 80: s = s[:80]
        print type(x),"\nGARBAGE OBJECTS:  ", s




    ########################################	########################################	########################################	########################################	########################################
# start proram, init variables and call loop
    ########################################	########################################	########################################	########################################	########################################

global PLOT, oldPLOT
global   noOfDays, numberOfMinutesInTimeBins, numberOfTimeTypes, numberOfTimeBins, dataColumnCount
global plotSizeNames, plotTimeNames, timeDataNumbers, dataVersion, parameterVersion,debugEnable
global indigoPlotDataDir, parameterFile, parameterFileD, indigoPNGdir, indigoPath
global myPID, msgCount, logHandle, quitNOW
global noOfMinutesInTimeBins
global eventData, eventIndex, DEVICE, dataColumnToDevice0Prop1Index

numberOfTimeTypes			=	3

msgCount					= 	0
quitNOW						=	False

plotSizeNames				=	["S1","S2"] # file names for size 1 and size 2 of plots
plotTimeNames				=	["minute","hour","day"] # files name for the different binings
noOfMinutesInTimeBins		=	[5,60,24*60]


userName					= pwd.getpwuid( os.getuid() )[ 0 ]
MAChome                     = os.path.expanduser("~")
indigoPlotDataDir			= MAChome+"/indigo/INDIGOPlotD/"  #  this is the data directory

parameterFile				= indigoPlotDataDir+"matplot/matplot.cfg"			# this is the config file name + -plot.cfg and -device.cfg
parameterFileD				= indigoPlotDataDir+"matplot/matplotD.cfg"			# this is the config file name + -plot.cfg and -device.cfg
matplotcommand				= indigoPlotDataDir+"matplot/matplot.cmd"
matplotlog					= indigoPlotDataDir+"matplot/matplot.log"
matplotlog1					= indigoPlotDataDir+"matplot/matplot1.log"
myPID						= str(os.getpid())
logHandle					= open( matplotlog , "a")
if not os.path.isdir( indigoPlotDataDir ): 	quitNOW = True

sendToLog(" ",level=1)
sendToLog("INDIGO matplot started Version 6.6",FULL= True,level=1)


PLOT={}

# kill old program if still running..
try:
    pidHandle= open( indigoPlotDataDir+"matplot/matplot.pid" , "r")
    oldPID = pidHandle.readline()
    pidHandle.close()
    if str(myPID) != oldPID:
        sendToLog("killing old python matplot instance ,pid: "+str(oldPID),FULL=True,level=1)
        if int(oldPID) > 0:	os.kill(int(oldPID), signal.SIGKILL)
except:
    pass
# register new pid for next time
pidHandle= open( indigoPlotDataDir+"matplot/matplot.pid" , "w")
pidHandle.write(str(myPID))
pidHandle.close()


fileData=[]
fileData.append(indigoPlotDataDir+"data/"+plotTimeNames[0]+".dat") # data file names
fileData.append(indigoPlotDataDir+"data/"+plotTimeNames[1]+".dat")
fileData.append(indigoPlotDataDir+"data/"+plotTimeNames[2]+".dat")


# find the latest indigo version number and path to indigo directories
found=False
indigoVersion = 0
for indi in range(5,100):  # we are optimistic for the future of indigo, starting with V5
    if found:
        if os.path.isdir("/Library/Application Support/Perceptive Automation/Indigo "+str(indi)): continue
        else:
            indigoVersion = indi-1
            break
    else:
        if os.path.isdir("/Library/Application Support/Perceptive Automation/Indigo "+str(indi)): found = True
    
indigoPath	=	"/Library/Application Support/Perceptive Automation/Indigo "+str(indigoVersion)+"/"




if __name__ == "__main__":
    main()
exit()
