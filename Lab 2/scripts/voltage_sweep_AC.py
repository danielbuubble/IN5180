import pyvisa
import numpy as np
import time
import argparse
import matplotlib.pyplot as plt

def exisiting_tool(rm, lab_num, tool, socket_num):
    resource = rm.open_resource(f"TCPIP::nano-slab-{lab_num}-{tool}.uio.no::{socket_num}::SOCKET")
    resource.read_termination = '\n'
    if tool != "gpp":
        resource.write_termination = '\n'
    print(resource.query('*IDN?'))
    return resource

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Setting a frequency sweep with the MFG and reading it with the MDO")
    parser.add_argument("--slab_num", required=True, type=int, help="Lab space number between 1 and 6")
    parser.add_argument("--mfg_output_port", required=True, type=int, help="MFG output port, 1 or 2")
    parser.add_argument("--mdo_input_port_in", required=True, type=int, help="MDO input channel for input signal")
    parser.add_argument("--mdo_input_port_out", required=True, type=int, help="MDO input channel for output signal")
    parser.add_argument("--start_frequency", required=True, type=float, help="Sweep start frequency")
    parser.add_argument("--stop_frequency", required=True, type=float, help="Sweep stop frequency")
    parser.add_argument("--sweep_time", required=True, type=float, help="Total sweep duration in seconds")
    parser.add_argument("--amplitude", required=True, type=float, help="Signal amplitude")
    parser.add_argument("--offset", required=True, type=float, help="Signal offset")

    args = parser.parse_args()

    rm = pyvisa.ResourceManager()
    rm.list_resources()

    mfg = exisiting_tool(rm, args.slab_num, "mfg", 1026)
    osc = exisiting_tool(rm, args.slab_num, "mdo", 3000)

    # Prepare arrays to store measurements
    in_freq_values = []
    in_amp_values = []
    out_freq_values = []
    out_amp_values = []
    phase_shift = []

    # Configure the MFG Sweep
    mfg.write(f'OUTPUT{args.mfg_output_port}:LOAD INF')
    mfg.write(f'SOURCE{args.mfg_output_port}:APPL:SIN {args.start_frequency},{args.amplitude},{args.offset}')
    mfg.write(f'SOURCE{args.mfg_output_port}:FREQ:START {args.start_frequency}')
    mfg.write(f'SOURCE{args.mfg_output_port}:FREQ:STOP {args.stop_frequency}')
    mfg.write(f'SOURCE{args.mfg_output_port}:SWEEP:SPACING LOG')
    mfg.write(f'SOURCE{args.mfg_output_port}:SWEEP:TIME {args.sweep_time}')
    mfg.write(f'SOURCE{args.mfg_output_port}:SWEEP:STATE ON')  # Correct command to start sweep
    mfg.write(f'OUTPUT{args.mfg_output_port} ON')  # Enable output

    prev_frequency = float('inf')  # Initialize to something higher than max expected frequency
    while True:
        # Wait for autoscale to finish
        osc.write(':AUTOSet')
        time.sleep(0.5)  # Adjust as necessary

        # Input measurement
        osc.write(f':CHANnel{args.mdo_input_port_in}:DISPlay ON')
        osc.write(':MEASure:SOURCE CH{args.mdo_input_port_in}')
        
        current_frequency = osc.write(':MEASure:FREQuency?')
        current_amplitude = float(osc.query(':measure:amplitude?'))
        
        in_freq_values.append(current_frequency)
        in_amp_values.append(current_amplitude)
        
        time.sleep(0.5)

        # Output measurement
        osc.write(f':CHANnel{args.mdo_input_port_out}:DISPlay ON')
        osc.write(f':measure:source2 CH{args.mdo_input_port_out}')
        
        current_frequency_out = float(osc.query(':measure:frequency?'))
        current_amplitude_out = float(osc.query(':measure:amplitude?'))
        
        out_freq_values.append(current_frequency_out)
        out_amp_values.append(current_amplitude_out)
        
        time.sleep(0.5)

        # Phase difference measurement:
        osc.write(f':measure:source1 CH{args.mdo_input_port_in}')  # e.g., CH1
        osc.write(f':measure:source2 CH{args.mdo_input_port_out}')  # e.g., CH2
        
        current_phase_shift = float(osc.query('measure:phase?'))
        
        phase_shift.append(current_phase_shift)
        print(f'Phase difference: {current_phase_shift}')

        # Check if the sweep has completed
        if current_frequency >= prev_frequency:
            prev_frequency = current_frequency
        else:
            break  # Exit the loop if the frequency is lower than the previous

    print(f'Phase shift: {phase_shift}')
    # Sweep Off
    mfg.write(f'SOURCE{args.mfg_output_port}:FREQ:SWEEP:STATE OFF')
    mfg.write(f'OUTPUT{args.mfg_output_port} OFF')

    # Plot or process data
    plt.plot(in_freq_values, phase_shift, label="Phase Shift")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Phase Shift (degrees)")
    plt.legend()
    plt.show()
