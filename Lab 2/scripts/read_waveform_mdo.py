import pyvisa
import numpy as np
import time
import argparse
import matplotlib.pyplot as plt

def existing_tool(rm, lab_num, tool, socket_num):
    fung = rm.open_resource(f"TCPIP::nano-slab-{lab_num}-{tool}.uio.no::{socket_num}::SOCKET")
    fung.read_termination = '\n'
    if tool != "gpp":
        fung.write_termination = '\n'
    fung.timeout = 20000  # Increase timeout to 20 seconds
    print(fung.query('*IDN?'))
    return fung

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Measure opamp frequency response")
    parser.add_argument('--slab_num', type=int, required=True, help='Lab number')
    parser.add_argument('--mfg_output_port', type=int, required=True, help='MFG output port')
    parser.add_argument('--mdo_input_port_in', type=int, required=True, help='MDO input channel for opamp input')
    parser.add_argument('--mdo_input_port_out', type=int, required=True, help='MDO input channel for opamp output')
    parser.add_argument('--frequency_min', type=float, required=True, help='Minimum frequency')
    parser.add_argument('--frequency_max', type=float, required=True, help='Maximum frequency')
    parser.add_argument('--num_points', type=int, required=True, help='Number of sweep points')
    parser.add_argument('--amplitude', type=float, required=True, help='Signal amplitude')
    parser.add_argument('--offset', type=float, required=True, help='Signal offset')

    args = parser.parse_args()

    rm = pyvisa.ResourceManager()
    rm.list_resources()

    # Connecting to instruments
    mfg = existing_tool(rm, args.slab_num, "mfg", 1026)
    osc = existing_tool(rm, args.slab_num, "mdo", 3000)

    # Configure MFG as sine wave generator
    mfg.write(f"OUTPUT{args.mfg_output_port}:LOAD INF")
    mfg.write(f"SOURCE{args.mfg_output_port}:FUNCTION SIN")
    mfg.write(f"SOURCE{args.mfg_output_port}:VOLTAGE {args.amplitude}")
    mfg.write(f"SOURCE{args.mfg_output_port}:VOLTAGE:OFFSET {args.offset}")
    mfg.write(f"SOURCE{args.mfg_output_port}:FREQUENCY {args.frequency_min}")
    
    # Configure oscilloscope inputs
    osc.write(f":CHANNEL{args.mdo_input_port_in}:DISPLAY ON")
    osc.write(f":CHANNEL{args.mdo_input_port_out}:DISPLAY ON")
    osc.write(":TIMEBASE:SCALE AUTO")

    # Frequency sweep setup
    frequencies = np.logspace(np.log10(args.frequency_min), np.log10(args.frequency_max), args.num_points)
    gain = np.empty(frequencies.size)
    phase_shift = np.empty(frequencies.size)

    i = 0
    for freq in frequencies:
        mfg.write(f"SOURCE{args.mfg_output_port}:FREQUENCY {freq}")
        # Wait for output signal to settle
        time.sleep(2)  # Adjust this delay as necessary

        # Autoscale oscilloscope
        osc.write(":AUTOSCALE")
        time.sleep(1)  # Allow oscilloscope to autoscale

        # Measure input voltage
        osc.write(f":MEASure:SOURce1 CHANnel{args.mdo_input_port_in}")
        time.sleep(0.5)
        vpp_in = float(osc.query(":MEASure:amplitude?"))

        # Measure output voltage
        osc.write(f":MEASure:SOURce1 CHANnel{args.mdo_input_port_out}")
        time.sleep(0.5)
        vpp_out = float(osc.query(":MEASure:amplitude?"))

        # Compute gain and phase shift
        if vpp_in != 0:
            gain_value = 20 * np.log10(vpp_out / vpp_in)
        else:
            gain_value = 0

        # Measure phase difference directly if the oscilloscope supports it
        # Measure phase difference
        osc.write(f":MEASure:SOURce1 CHANnel{args.mdo_input_port_in}")
        osc.write(f":MEASure:SOURce2 CHANnel{args.mdo_input_port_out}")
        time.sleep(0.5)
        phase_shift[i] = osc.query(":MEASure:PHASe?")
        gain[i] = gain_value
        i += 1

        

    

    unity_gain_freq = frequencies[np.argmin(np.abs(gain))]
    phase_margin = 180 + np.interp(unity_gain_freq, frequencies, phase_shift)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    ax1.semilogx(frequencies, gain, label='Gain')
    ax1.set_title('Bode Plot')
    ax1.set_xlabel('Frequency [Hz]')
    ax1.set_ylabel('Gain [dB]')
    ax1.axvline(unity_gain_freq, color='r', linestyle='--', label=f'Unity Gain Freq: {unity_gain_freq:.2f} Hz')
    ax1.legend()
    ax1.grid(True)

    ax2.semilogx(frequencies, phase_shift, label='Phase Shift')
    ax2.set_xlabel('Frequency [Hz]')
    ax2.set_ylabel('Phase Shift [Degrees]')
    ax2.axhline(phase_margin, color='g', linestyle='--', label=f'Phase Margin: {phase_margin:.2f} degrees')
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.show()
