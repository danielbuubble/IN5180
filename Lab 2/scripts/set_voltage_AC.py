import pyvisa
import argparse
import time

#Function for checking if tool is available
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
    parser.add_argument("--mfg_output_port", required=True, type=int, help="Which of the MFG channels is used, 1 or 2")
    parser.add_argument("--mdo_input_port", required=True, type=int, help="Osillosccope input channel")
    parser.add_argument("--frequency", required=True, type=float, help="MFG output frequency")
    parser.add_argument("--amplitude", required=True, type=float, help="MFG output amplitude")
    parser.add_argument("--offset", required=True, type=float, help="MFG output DC offset")
    
    args = parser.parse_args()

    #Invoking the resources
    rm = pyvisa.ResourceManager()
    rm.list_resources()
	
    mfg = exisiting_tool(args.slab_num,"mfg",1026)
    osc = exisiting_tool(args.slab_num,"mdo",3000)
        
    #Set otuput load of MFG to high impedanze
    mfg.write('output'+str(args.mfg_output_port)+':load inf')
    #Set signal for mfg:
    mfg.write('source'+str(args.mfg_output_port)+':appl:sin '+str(args.frequency)+','+str(args.amplitude)+','+str(args.offset))
    #Wait for valid output from the mfg: 
    time.sleep(10)

    
    # Select channel(s) for measurement:
    osc.write(':CHANnel'+str(args.mdo_input_port)+':DISPlay ON')
    print(osc.query(':CHANnel'+str(args.mdo_input_port)+':DISPlay?'))
    osc.write(':measure:source1 CH'+str(args.mdo_input_port)) 
    
    print(osc.query(':measure:frequency?'))
    print(osc.query(':measure:amplitude?'))
    
    # Turns channel off after use
    #osc.write(':CHANnel'+str(args.mdo_input_port)+':DISPlay OFF')
    
    
    '''
    #Phase difference measurement:
    osc.write(':CHANnel'+str(args.mdo_input_port1)+':DISPlay ON')
    osc.write(':CHANnel'+str(args.mdo_input_port2)+':DISPlay ON')
    osc.write(':measure:source1 CH'+str(args.mdo_input_port_1)) #eg CH1
    osc.write(':measure:source2 CH'+str(args.mdo_input_port_2)) #eg CH2
    print(osc.query('measure:phase?')
    '''
    
    '''
    #Aquire data
    osc.write(':acquire:mode sample')
    osc.write(':header ON')
    osc.write(':acquire:recordlength 1e+4') 
    
    while(os.query(':acquire1:state?')==0):
        time.sleep(10)
    data = osc.query(':acquire:memory?')
    
    '''