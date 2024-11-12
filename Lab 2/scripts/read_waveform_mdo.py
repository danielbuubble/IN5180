import pyvisa
import numpy as np
import matplotlib.pyplot as plt
import time
import argparse

def existing_tool(rm, lab_num, tool, socket_num):
    resource_string = f"TCPIP::nano-slab-{lab_num}-{tool}.uio.no::{socket_num}::SOCKET"
    fung = rm.open_resource(resource_string)
    fung.read_termination = '\n'
    fung.write_termination = '\n'
    print(fung.query('*IDN?'))
    return fung

def process_data(raw_data, sampling_rate):
    data = np.array(raw_data)
    data_no_offset = data - np.mean(data)
    window = np.hanning(len(data_no_offset))
    windowed_data = data_no_offset * window
    fft_result = np.fft.fft(windowed_data)
    magnitudes = np.abs(fft_result[:len(fft_result)//2])
    phases = np.unwrap(np.angle(fft_result[:len(fft_result)//2]))
    freqs = np.fft.fftfreq(len(fft_result), d=1/sampling_rate)[:len(fft_result)//2]
    return freqs, magnitudes, phases

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Measure opamp frequency response")
    parser.add_argument('--slab_num', type=int, required=True, help='Lab number')
    parser.add_argument('--mfg_output_port', type=int, required=True, help='MFG output port')
    parser.add_argument('--mdo_input_port_in', type=int, required=True, help='MDO input channel for opamp input')
    parser.add_argument('--mdo_input_port_out', type=int, required=True, help='MDO input channel for opamp output')
    parser.add_argument('--waveform_type', type=str, required=True, help='Waveform type, e.g., sine')
    parser.add_argument('--frequency_min', type=float, required=True, help='Minimum frequency')
    parser.add_argument('--frequency_max', type=float, required=True, help='Maximum frequency')
    parser.add_argument('--num_points', type=int, required=True, help='Number of sweep points')
    parser.add_argument('--amplitude', type=float, required=True, help='Signal amplitude')
    parser.add_argument('--offset', type=float, required=True, help='Signal offset')
    
    args = parser.parse_args()

    rm = pyvisa.ResourceManager()
    rm.list_resources()

    mfg = existing_tool(rm, args.slab_num, "mfg", 1026)
    osc = existing_tool(rm, args.slab_num, "mdo", 3000)

    # Configure MFG
    mfg.write(f"SOURCE{args.mfg_output_port}:FUNCTION {args.waveform_type}")
    mfg.write(f"SOURCE{args.mfg_output_port}:VOLTAGE {args.amplitude}")
    mfg.write(f"SOURCE{args.mfg_output_port}:VOLTAGE:OFFSET {args.offset}")
    
    # Configure oscilloscope inputs
    osc.write(f":CHANNEL{args.mdo_input_port_in}:DISPLAY ON")
    osc.write(f":CHANNEL{args.mdo_input_port_out}:DISPLAY ON")
    osc.write(":TIMEBASE:SCALE AUTO")
    
    frequencies = np.logspace(np.log10(args.frequency_min), np.log10(args.frequency_max), args.num_points)
    gain = []
    phase_shift = []
    sampling_rate = 1e6  # Adjust according to your actual oscilloscope's setting

    try:
        for freq in frequencies:
            mfg.write(f"SOURCE{args.mfg_output_port}:FREQUENCY {freq}")
            time.sleep(1)  # Allow signal to settle

            osc.write(":AUTOSCALE")

            # Acquire waveforms
            osc.write(f":WAVeform:SOURce CHANNEL{args.mdo_input_port_in}")
            osc.write(":WAVeform:FORMat ASCII")
            input_waveform = osc.query(":WAVeform:DATA?")
            input_data = list(map(float, input_waveform.split(',')))

            osc.write(f":WAVeform:SOURce CHANNEL{args.mdo_input_port_out}")
            osc.write(":WAVeform:FORMat ASCII")
            output_waveform = osc.query(":WAVeform:DATA?")
            output_data = list(map(float, output_waveform.split(',')))

            # Process data
            freqs_in, mag_in, phase_in = process_data(input_data, sampling_rate)
            freqs_out, mag_out, phase_out = process_data(output_data, sampling_rate)

            idx = np.argmin(np.abs(freqs_in - freq))
            gain_value = 20 * np.log10(mag_out[idx] / mag_in[idx])
            phase_value = (phase_out[idx] - phase_in[idx]) * 180 / np.pi

            gain.append(gain_value)
            phase_shift.append(phase_value)

        gain = np.array(gain)
        phase_shift = np.array(phase_shift)

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

    except pyvisa.errors.VisaIOError as e:
        print(f"An error occurred while communicating with the instrument: {e}")
        print("Please check your connection settings and try again.")
        exit(1)
