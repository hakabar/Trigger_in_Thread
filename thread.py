
import threading
from PyDAQmx import *
from PyDAQmx.DAQmxTypes import *
import numpy as np
import logging
import time


logging.basicConfig(level=logging.DEBUG,format='[%(levelname)s] (%(threadName)-10s) %(message)s',)


def writeDigital():
    """thread to write an digital output in NI USB 6008"""
    logging.debug('Starting')
    #Declaration of variables
    #data = np.array([0,1,1,0,1,0,1,0], dtype=np.uint32)
    pulse = np.zeros(1, dtype=np.uint8)
    pulse[0]=1
    
    #DAQ Start Code
    digital_output = Task()
    
    #DAQ Configuration Code
    digital_output.CreateDOChan("/Dev1/port1/line1","",DAQmx_Val_ChanForAllLines)
    
    digital_output.StartTask()
    #send one second 0/1pulses during 8 seconds
    start_time=time.time()
    while ((time.time()-start_time) < 2.0):
        digital_output.WriteDigitalLines(1,1,5.0,DAQmx_Val_GroupByChannel,pulse,None,None)
        time.sleep(0.5)
        pulse[0]=abs(pulse[0]-1)
        #digital_output.WriteDigitalLines(1,1,5.0,DAQmx_Val_GroupByChannel,pulse,None,None)
    #DAQ Stop Code
    digital_output.StopTask()
    
    logging.debug('Exiting')
#    print 'write analog output'
#    return

def readDigital():
    """thread to read an digital input in NI USB 6008"""
    logging.debug('Starting')
    
    #Declaration of variable passed by reference
    digital_input = Task()
    sampsPerChanRead = int32()
    numBytesPerSamp = int32()
    #data = numpy.zeros(1, dtype=numpy.uint32)
    #pulse = np.zeros(1, dtype=np.uint8)
    pulse = np.zeros((1,), dtype=np.uint8)
    pulse[0]=0
    count_loop=0
    old_value=999

    #DAQ Configuration Code
    digital_input.CreateDIChan("Dev1/port0/line4","", DAQmx_Val_GroupByChannel)
    
    #DAQmx Start Code
    digital_input.StartTask()
    

    start_read=time.time()
    print "Acquiring samples during 2.5 seconds. start_read: %d\n"%start_read
    while ((time.time()-start_read) < 2.5):
        #DAQmx Read Code
        #args= (taskHandler (1=taskHandle, 1= numSampsPerChan, DAQmx_Val_WaitInfinitely= timeout, DAQmx_Val_GroupByChannel= fillMode,
        #       pulse= readArray[], len(pulse)= arraySizeInBytes, None= sampsPerChanRead, None=numBytesPerSamp, None= Reseved(not used) )
        #status= digital_input.ReadDigitalLines(1,1,DAQmx_Val_WaitInfinitely,DAQmx_Val_GroupByChannel,pulse,len(pulse),sampsPerChanRead,numBytesPerSamp)
        digital_input.ReadDigitalLines(1,-1, DAQmx_Val_GroupByChannel, pulse, 1,byref(sampsPerChanRead), byref(numBytesPerSamp), None)
        #digital_input.ReadDigitalLines(1,1,5.0,DAQmx_Val_GroupByChannel,None,pulse,byref(sampsPerChanRead),byref(numBytesPerSamp))
        #digital_input.ReadDigitalU32(-1, 1, DAQmx_Val_GroupByChannel, data, 1000, byref(read), None)
        if pulse[0] != old_value:
            print "reading: %d"%pulse[0] 
            old_value= pulse[0]
        count_loop+=1
        #print "status: %d"%status
        

    #DAQ Stop Code
    digital_input.StopTask()
    logging.debug('Exiting')

t_output = threading.Thread(name= 'Write_Digital_Output', target=writeDigital)
t_input = threading.Thread(name='Read_Digital_Input', target=readDigital)

print "STARTING DAQ with NI USB6008"
t_input.start()
time.sleep(0.25)
t_output.start()
