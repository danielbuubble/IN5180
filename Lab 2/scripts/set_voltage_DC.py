import pyvisa
import time
import numpy as np
import argparse

#Checking of tool is available
def exisiting_tool(lab_num,tool,soccet_num):
    fung = rm.open_resource("TCPIP::nano-slab-"+str(lab_num)+"-"+tool+".uio.no::"+str(soccet_num)+"::SOCKET")
    fung.read_termination = '\n'
    if(tool == "gpp"):
        pass 
    else:
        fung.write_termination = '\n'
    print(fung.query('*IDN?'))
    return fung

if (__name__ == "__main__"):
    parser = argparse.ArgumentParser(
        description="Setting a DC voltage with the power supply (gpp) and reading it with the digital multimeter(gdm)"
    )
    parser.add_argument("--slab_num", required=True, type=int, help="Lab space number between 1 and 6")
    parser.add_argument("--voltage1", required=True, type=float, help="Voltage for output 1")
    parser.add_argument("--voltage2", required=True, type=float, help="Voltage for output 2")
    args = parser.parse_args()

    #Invoking the resources
    rm = pyvisa.ResourceManager()
    rm.list_resources()

    #Check if tools are available:    
    dcpp = exisiting_tool(args.slab_num,"gpp",1026)
    dmm  = exisiting_tool(args.slab_num,"gdm",3001)

    #Set DC voltage for each of the two channels:
    dcpp.write('VSET1:'+str(args.voltage1)) #This works
    dcpp.write('VSET2:'+str(args.voltage2)) #This works

    #Checking if the correct votlages are set:
    print('The set voltages:')
    print(dcpp.query(':source1:voltage?'))
    print(dcpp.query(':source2:voltage?'))

    #Activating outputs
    dcpp.write(':output1:state on')
    dcpp.write(':output2:state on')
    
    #Measuring the set voltages:
    print(dmm.query('measure:voltage:DC?'))

