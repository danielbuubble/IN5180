import pyvisa
import numpy as np
import time
import argparse
import matplotlib.pyplot as plt

def exisiting_tool(lab_num,tool,socket_num):
    fung = rm.open_resource("TCPIP::nano-slab-"+str(lab_num)+"-"+tool+".uio.no::"+str(socket_num)+"::SOCKET")
    fung.read_termination = '\n'
    if(tool == "gpp"):
        pass 
    else:
        fung.write_termination = '\n'
    print(fung.query('*IDN?'))
    return fung

if (__name__=="__main__"):
    #Parser for the input arguments
    parser = argparse.ArgumentParser(description="Setting a frequency sweep with the MFG and reading it with the MDO")
    parser.add_argument("--slab_num", required=True, type=int, help="Lab space number between 1 and 6")
    parser.add_argument("--mfg_output_port", required=True, type=int, help="Which of the MFG channels is used, 1 or 2")
    parser.add_argument("--mdo_input_port_in", required=True, type=int, help="Oscilloscope  channel to read the input")
    parser.add_argument("--mdo_input_port_out", required=True, type=int, help="Oscilloscope channel to read the output")
    parser.add_argument("--start_frequency", required=True, type=float, help="Start frequency of the sweep for the MFG")
    parser.add_argument("--stop_frequency", required=True, type=float, help="Stop frequency of the sweep for the MFG")
    parser.add_argument("--steps", required=True, type=int, help="Number of steps in the frequency sweep")
    parser.add_argument("--amplitude", required=True, type=float, help="Amplitude of the signal")
    parser.add_argument("--offset", required=True, type=float, help="Offset of the signal")

    args = parser.parse_args()

    #Invoking the resources
    rm = pyvisa.ResourceManager()
    rm.list_resources()

    mfg = exisiting_tool(args.slab_num,"mfg",1026)
    osc = exisiting_tool(args.slab_num,"mdo",3000)

    #Setting up the MFG
    #Set otuput load of MFG to high impedance

    #Set signal for mfg:
    sweep_values = np.array([args.start_frequency *(args.stop_frequency/args.start_frequency)**(i/(args.steps-1)) for i in range(1, args.steps + 1)])

    in_freq_values = np.empty(sweep_values.size)
    in_amp_values = np.empty(sweep_values.size)
    out_freq_values = np.empty(sweep_values.size)
    out_amp_values = np.empty(sweep_values.size)
    phase_shift = np.empty(sweep_values.size)
    print('Number of steps: '+str(sweep_values.size))

    i = 0
    for x in sweep_values:
        #Set signal for mfg:
        mfg.write('output '+str(args.mfg_output_port)+':load inf')
        mfg.write('source '+str(args.mfg_output_port)+':appl:sin '+str(x)+','+str(args.amplitude)+','+str(args.offset))
        mfg.write('SOURce1:PHASe 0')
        mfg.write('SOURce2:PHASe 0')
        print('Cnt: '+str(i)+' Frequency: '+str(x))
        #Wait for valid output from the mfg:
        time.sleep(5)

        #Input measurement
        osc.write(':CHANnel'+str(args.mdo_input_port_in)+':DISPlay ON')
        osc.write(':measure:source1 CH'+str(args.mdo_input_port_in))
        in_freq_values[i] = osc.write(':measure:frequency?')
        in_amp_values[i] = osc.write(':measure:amplitude?')
        time.sleep(0.5)

        #Output measurement
        osc.write(':CHANnel'+str(args.mdo_input_port_out)+':DISPlay ON')
        osc.write(':measure:source2 CH'+str(args.mdo_input_port_out))
        out_freq_values[i] = osc.write(':measure:frequency?')
        out_amp_values[i] = osc.write(':measure:amplitude?')
        time.sleep(0.5)

        #Phase difference measurement:
        osc.write(':CHANnel'+str(args.mdo_input_port_in)+':DISPlay ON')
        osc.write(':CHANnel'+str(args.mdo_input_port_out)+':DISPlay ON')
        osc.write(':measure:source1 CH'+str(args.mdo_input_port_in)) #eg CH1
        osc.write(':measure:source2 CH'+str(args.mdo_input_port_out)) #eg CH2
        phase_shift[i] = osc.write('measure:phase?')
        time.sleep(0.5)
        i = i + 1
    
    print(phase_shift)