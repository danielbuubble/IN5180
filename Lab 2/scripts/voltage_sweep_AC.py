import pyvisa
import numpy as np
import time
import argparse
import matplotlib.pyplot as plt

def exisiting_tool(lab_num, tool, socket_num):
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

    mfg = exisiting_tool(args.slab_num, "mfg", 1026)
    osc = exisiting_tool(args.slab_num, "mdo", 3000)

    # Configure the MFG Sweep
    mfg.write(f'OUTPUT{args.mfg_output_port}:LOAD INF')
    mfg.write(f'SOURCE{args.mfg_output_port}:APPL:SIN {args.start_frequency},{args.amplitude},{args.offset}')
    mfg.write(f'SOURCE{args.mfg_output_port}:FREQ:START {args.start_frequency}')
    mfg.write(f'SOURCE{args.mfg_output_port}:FREQ:STOP {args.stop_frequency}')
    mfg.write(f'SOURCE{args.mfg_output_port}:SWEEP:SPACING LOG')
    mfg.write(f'SOURCE{args.mfg_output_port}:SWEEP:TIME {args.sweep_time}')
    mfg.write(f'SOURCE{args.mfg_output_port}:SWEEP:STATE ON')  # Start sweep
    mfg.write(f'OUTPUT{args.mfg_output_port} ON')  # Enable output

    # Prepare arrays to store measurements
    num_steps = int(args.sweep_time * 10)  # Adjust as needed for sampling rate
    in_freq_values = np.empty(num_steps)
    in_amp_values = np.empty(num_steps)
    out_freq_values = np.empty(num_steps)
    out_amp_values = np.empty(num_steps)
    phase_shift = np.empty(num_steps)

    highest_freq = 0
    i = 0
    # Acquire data at each step
    while(1):
        # Wait for autoscale to finish
        osc.write(':AUTOSET')
        time.sleep((args.sweep_time / num_steps) / 2)

        # Set MDO measurements for input
        osc.write(f':CHANnel{args.mdo_input_port_in}:DISPlay ON')
        osc.write(f':measure:source1 CH{args.mdo_input_port_in}')
        in_freq_values[i] = osc.write(':measure:frequency?')
        in_amp_values[i] = osc.write(':measure:amplitude?')
        print(f'Cnt: {i} Frequency: {in_freq_values[i]}')
        time.sleep(0.5)
        if in_freq_values[i] > highest_freq:
            highest_freq = in_freq_values[i]

        # Set MDO measurements for output
        osc.write(f':CHANnel{args.mdo_input_port_out}:DISPlay ON')
        osc.write(f':measure:source2 CH{args.mdo_input_port_out}')
        out_freq_values[i] = osc.write(':measure:frequency?')
        out_amp_values[i] = osc.write(':measure:amplitude?')

        print(f'Amp_in: {in_amp_values[i]} Amp_out: {out_amp_values[i]}')
        time.sleep(0.5)

        # Measure phase shift
        osc.write(f':CHANnel{args.mdo_input_port_in}:DISPlay ON')
        osc.write(f':CHANnel{args.mdo_input_port_out}:DISPlay ON')
        osc.write(f':measure:source1 CH{args.mdo_input_port_in}')
        osc.write(f':measure:source2 CH{args.mdo_input_port_out}')
        phase_shift[i] = osc.write('measure:phase?')

        i += 1
        time.sleep((args.sweep_time / num_steps) / 2)  # Wait for the next step

    # Turn off the output after one sweep
    mfg.write(f'SOURCE{args.mfg_output_port}:SWEEP:STATE OFF')
    mfg.write(f'OUTPUT{args.mfg_output_port} OFF')
    # Plot or process data
    plt.plot(in_freq_values, phase_shift, label="Phase Shift")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Phase Shift (degrees)")
    plt.legend()
    plt.show()
