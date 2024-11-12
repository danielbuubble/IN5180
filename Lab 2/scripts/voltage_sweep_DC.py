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
    parser.add_argument("--output_port", required=True, type=int, help="Which output should be swept, 1 or 2")
    parser.add_argument("--voltage_min", required=True, type=float, help="Lower bound for voltage sweep")
    parser.add_argument("--voltage_max", required=True, type=float, help="Upper bound for voltage sweep")
    parser.add_argument("--voltage_step", required=True, type=float, help="Voltage step for votlage sweep")
    args = parser.parse_args()

    #Invoking the resources
    rm = pyvisa.ResourceManager()
    rm.list_resources()
	
    #Check if tools are available:    
    dcpp = exisiting_tool(args.slab_num,"gpp",1026)
    dmm  = exisiting_tool(args.slab_num,"gdm",3001)

    #Setting up the instruments:
    dcpp.write('VSET'+str(args.output_port)+':'+str(args.voltage_min)) #This works
    
    #Activating outputs
    dcpp.write(':output'+str(args.output_port)+':state on')
    
    # DC sweep:
    set_values = np.arange(args.voltage_min, args.voltage_max+args.voltage_step*0.45, args.voltage_step) # sweep parameters
    meas_values = np.empty(set_values.size)
    print('Number of steps: '+str(set_values.size))
    print(args.output_port)
    
    i = 0
    for x in set_values:
        dcpp.write('VSET'+str(args.output_port)+':'+str(x))
        print('Cnt: '+str(i)+' Voltage: '+str(x))
        time.sleep(10)
        meas_values[i] = dmm.query('measure:voltage:DC?')
        time.sleep(5)
        i = i + 1
        
    
    dcpp.write(':output'+str(args.slab_num)+':state off')
    print(meas_values)
    
