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
    parser.add_argument("--mfg_output_port", required=True, type=int, help="MFG output port, 1 or 2")
    parser.add_argument("--mdo_input_port_in", required=True, type=int, help="MDO input channel for input signal")
    parser.add_argument("--mdo_input_port_out", required=True, type=int, help="MDO input channel for output signal")
    parser.add_argument("--frequency", required=True, type=float, help="MFG output frequency")
    parser.add_argument("--amplitude", required=True, type=float, help="MFG output amplitude")
    parser.add_argument("--offset", required=True, type=float, help="MFG output DC offset")
    parser.add_argument("--phase", required=True, type=float, help="MFG phase difference")
    
    args = parser.parse_args()

    #Invoking the resources
    rm = pyvisa.ResourceManager()
    rm.list_resources()
	
    mfg = exisiting_tool(args.slab_num,"mfg",1026)
    osc = exisiting_tool(args.slab_num,"mdo",3000)
        
    #Set otuput load of MFG to high impedanze
    mfg.write(f'OUTPUT{args.mfg_output_port}:LOAD INF')
    mfg.write(f'SOURCE{args.mfg_output_port}:APPL:SIN {args.frequency},{args.amplitude},{args.offset}')
    osc.write(':AUTORSET:MODe FITScreen')
    #Wait for valid output from the mfg: 
    time.sleep(10)

    #osc.write(':CHANnel'+str(args.mdo_input_port_in)+':DISPlay ON')
    #osc.write(':measure:source1 CH'+str(args.mdo_input_port_in)) #eg CH1
    #print('InputFrequency: '+str(osc.query(':measure:frequency?')))
    #print('InputAmplitude: '+str(osc.query(':measure:amplitude?')))

    osc.write(':CHANnel'+str(args.mdo_input_port_out)+':DISPlay ON')
    osc.write(':measure:source'+str(args.mdo_input_port_out)+ ' CH'+str(args.mdo_input_port_out)) #eg CH2
    print('OutputFrequency: '+str(osc.query(':measure:frequency?')))
    print('OutputAmplitude: '+str(osc.query(':measure:amplitude?')))
    
    
    #Phase difference measurement:
    osc.write(':CHANnel'+str(args.mdo_input_port_out)+':DISPlay ON')
    osc.write(':CHANnel'+str(args.mdo_input_port_out)+':DISPlay ON')
    osc.write(':measure:source'+str(args.mdo_input_port_in)+ ' CH'+str(args.mdo_input_port_in)) #eg CH1
    osc.write(':measure:source2 CH'+str(args.mdo_input_port_out)) #eg CH2
    
    print('Phase difference: '+str(osc.query('measure:phase?')))

    
    '''
    #Aquire data
    osc.write(':acquire:mode sample')
    osc.write(':header ON')
    osc.write(':acquire:recordlength 1e+4') 
    
    while(os.query(':acquire1:state?')==0):
        time.sleep(10)
    data = osc.query(':acquire:memory?')
    
    '''