##
## MULTICOMP PRO MP730889 Library
##
## This library has been made to operate the basic functionalities of the MP730889
## such as connect, measure resistance, measure voltage, and few other functions
##
## Author : German G.
##


import pyvisa
from pyvisa.constants import StopBits, Parity

from math import isnan
import serial
import serial.tools.list_ports as port_list
from functools import wraps

#Constants initialization
TIMEOUT= 2
TERMINATION = "\n"
BAUD_RATE=115200   ## configured at the GPP4323
DATA_BITS=8      ## default at the GPP4323
DEVICE_DESCRIPTION = "COM22"
DEVICE_NAME = "MP730889"
DEBUG = True

#Variable initialization
I = "I"
V = "V"
v = "V"
i = "I"

## Connectivity error handler
def connectivity_error_handler(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except NameError as e:
            print(DEVICE_NAME+":ERROR.Device not connected.Use "+DEVICE_NAME+".connect() first")
        except AssertionError as e:
            print(DEVICE_NAME+":ERROR.Could not perform action.Check the device is correctly detected by the OS, or the connection parameters are adequate.")
        except AttributeError as e:
            print(DEVICE_NAME+":ERROR.Device not connected.Check the device is correctly detected by the OS, or the connection parameters are adequate.")
    return decorator

## Connects to the GPP4323. Since this device behaves as any random Serial port device,
## the connection settings must be specified.
     
def connect():
    global instrument
    print("BACKEND:****************************** SERIAL PORTS DETECTED ******************************")
    deviceport = "NULL"
    ports = list(port_list.comports())
    for p in ports:
        print(p.description)
        if "COM22" in p.description: # Arduino is currently replacing the FPGA
            deviceport = p.device
            print(DEVICE_NAME+":Correctly detected") 
            try:
                instrument = serial.Serial(deviceport, baudrate=BAUD_RATE, bytesize=DATA_BITS, timeout=TIMEOUT, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
            except:
                print("BACKEND:DISCONNECTED")
                
    if deviceport == "NULL": 
        print(DEVICE_NAME+":ERROR.Device not detected.Check connection cables, drivers or instrument at OS settings. Current instrument description:'"+DEVICE_DESCRIPTION+"'")
        return False

    print("BACKEND:*************************** AUTOMATIC DETECTION RESULTS ***************************")
    return True
     
     
def disconnect(): 
    global instrument
    response = instrument.close()
    return response
     
## Ask for the IDN of the device in VISA programming language 
## example command: INST_MPP730889.get_device_identity()

@connectivity_error_handler
def get_device_identity():
    global instrument
    command = "*IDN?"+'\r'+'\n'
    instrument.write(command.encode())
    #print("Sending: "+command )
    response = instrument.readline()
    return response.decode().splitlines()[0]

## measure commands
@connectivity_error_handler
def get_measurement(): # Get main measurement  
    global instrument
    command = "MEAS1?"+'\r'+'\n'
    instrument.write(command.encode())
    response = instrument.readline()
    #print(response)
    return response.decode().splitlines()[0]
    
def get_measurement2(): # Get secondary measurement, usually frequency in AC modes
    global instrument
    command = "MEAS2?"+'\r'+'\n'
    instrument.write(command.encode())
    response = instrument.readline()
    #print(response)
    return response.decode().splitlines()[0]

## Magnitude commands
def set_resistance_mode(scale = None):# set resistnace mode. If no scale is selected it is AUTO
    global instrument
    if scale not in [None,500,5E3,50E3,500E3,5E6,50E6,500E6]:
        print("Unexpected values: Valid values are empty,500,5E3,50E3,500E3,5E6,50E6,500E6")
        return False

    command = "CONF:RES "+str(scale)+'\r'+'\n'
    instrument.write(command.encode())
    
    if scale == None:
        set_autoscale_on()
    
    
def set_voltageDC_mode(scale = None):# set voltage DC mode. If no scale is selected it is AUTO
    global instrument
    if scale not in [None,50E-3,500E-3,5,50,500,1000]:
        print("Unexpected values: Valid values are empty,50E-3,500E-3,5,50,500,1000")
        return

    command = "CONF:VOLT:DC "+str(scale)+'\r'+'\n'
    instrument.write(command.encode())
    
    if scale == None:
        set_autoscale_on()

def set_voltageAC_mode(scale = None): # set voltage AC mode. If no scale is selected it is AUTO
    global instrument
    if scale not in [None,500E-3,5,50,500,750]:
        print("Unexpected values: Valid values are empty,500E-3,5,50,500,750")
        return

    command = "CONF:VOLT:AC "+str(scale)+'\r'+'\n'
    instrument.write(command.encode())
    
    if scale == None:
        set_autoscale_on()

## other commands
def set_autoscale_on(): # turn on autoscale
    global instrument
    command = "AUTO 1"+'\r'+'\n'
    instrument.write(command.encode())

def set_autoscale_off(): # turn off autoscale
    global instrument
    command = "AUTO 0"+'\r'+'\n'
    instrument.write(command.encode())
    
