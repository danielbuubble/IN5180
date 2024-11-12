import pyvisa
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import bode
import argparse

def exisiting_tool(lab_num, tool, socket_num):
    fung = rm.open_resource("TCPIP::nano-slab-"+str(lab_num)+"-"+tool+".uio.no::"+str(socket_num)+"::SOCKET")
    fung.read_termination = '\n'
    if tool == "gpp":
        pass
    else:
        fung.write_termination = '\n'
    print(fung.query('*IDN?'))
    return fung

def process_data(raw_data):
    # Convert raw data to numpy array if needed
    data = np.array(raw_data)
    
    # Remove DC offset
    data_no_offset = data - np.mean(data)
    
    # Apply windowing
    window = np.hanning(len(data_no_offset))
    windowed_data = data_no_offset * window
    
    # Perform FFT
    fft_result = np.fft.fft(windowed_data)
    
    # Get magnitudes and phases
    freqs = np.fft.fftfreq(len(fft_result)) * sampling_rate
    magnitudes = np.abs(fft_result)
    phases = np.unwrap(np.angle(fft_result))
    
    return freqs, magnitudes, phases

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Measure opamp frequency response")
    parser.add_argument("--slab_num", required=True, type=int, help="Lab space number")
    parser.add_argument("--mfg_output_port", required=True, type=int, help="MFG channel used")
    parser.add_argument("--mdo_input_port_in", required=True, type=int, help="MD0 input channel for input signal")
    parser.add_argument("--mdo_input_port_out", required=True, type=int, help="MD0 input channel for output signal")
    parser.add_argument("--frequency_min", required=True, type=float, help="Minimum frequency")
    parser.add_argument("--frequency_max", required=True, type=float, help="Maximum frequency")
    parser.add_argument("--num_points", required=True, type=int, help="Number of frequency points")
    parser.add_argument("--amplitude", required=False, type=float, default=100, help="Amplitude of input signal (default: 100)")
    parser.add_argument("--offset", required=False, type=float, default=0, help="Offset of input signal (default: 0)")
    
    args = parser.parse_args()

    rm = pyvisa.ResourceManager()
    rm.list_resources()

    mfg = exisiting_tool(args.slab_num, "mfg", 1026)
    osc_in = exisiting_tool(args.slab_num, "mdo", 3000)
    osc_out = exisiting_tool(args.slab_num, "mdo", 3001)

    # Configure MFG
    mfg.write(f"source{args.mfg_output_port}:apply sine {args.frequency_min},{args.amplitude},{args.offset}")
    
    # Configure oscilloscope inputs
    osc_in.write(f":input{args.mdo_input_port_in}:acquire off")
    osc_in.write(f":input{args.mdo_input_port_in}:acquire on")
    osc_out.write(f":input{args.mdo_input_port_out}:acquire off")
    osc_out.write(f":input{args.mdo_input_port_out}:acquire on")

    # Perform sweep
    frequencies = np.logspace(np.log10(args.frequency_min), np.log10(args.frequency_max), args.num_points)
    
    mag_data_in = np.zeros(len(frequencies))
    phase_data_in = np.zeros(len(frequencies))
    mag_data_out = np.zeros(len(frequencies))
    phase_data_out = np.zeros(len(frequencies))

    sampling_rate = 1e6  # Assuming 1 MHz sampling rate

    for i, freq in enumerate(frequencies):
        mfg.write(f"source{args.mfg_output_port}:frequency {freq}")
        
        while osc_in.query(":ACQuire"+str(args.mdo_input_port_in)+":STATe?") == "0":
            pass
        
        header = osc_in.query(":ACQuire"+str(args.mdo_input_port_in)+":MEMory?")
        data_in = osc_in.query("DISP:WAV? DAT:ASC")
        
        while osc_out.query(":ACQuire"+str(args.mdo_input_port_out)+":STATe?") == "0":
            pass
        
        header = osc_out.query(":ACQuire"+str(args.mdo_input_port_out)+":MEMory?")
        data_out = osc_out.query("DISP:WAV? DAT:ASC")
        
        freqs_in, magnitudes_in, phases_in = process_data(data_in)
        mag_data_in[i] = magnitudes_in
        phase_data_in[i] = phases_in
        
        freqs_out, magnitudes_out, phases_out = process_data(data_out)
        mag_data_out[i] = magnitudes_out
        phase_data_out[i] = phases_out

    w, mag_in = bode(frequencies, mag_data_in)
    w, mag_out = bode(frequencies, mag_data_out)
    
    unity_gain_index_in = np.argmin(np.abs(mag_in))
    unity_gain_freq_in = frequencies[unity_gain_index_in]
    
    phase_margin_in = 180 - np.max(phase_data_in) * 180 / np.pi

    w, mag_out = bode(frequencies, mag_data_out)
    unity_gain_index_out = np.argmin(np.abs(mag_out))
    unity_gain_freq_out = frequencies[unity_gain_index_out]
    
    phase_margin_out = 180 - np.max(phase_data_out) * 180 / np.pi

    plt.figure(figsize=(10,6))
    plt.semilogx(frequencies, 20*np.log10(mag_in), label='Input Magnitude')
    plt.semilogx(frequencies, phase_data_in*180/np.pi, label='Input Phase')
    plt.semilogx(frequencies, 20*np.log10(mag_out), label='Output Magnitude')
    plt.semilogx(frequencies, phase_data_out*180/np.pi, label='Output Phase')
    plt.axvline(unity_gain_freq_in, color='r', linestyle='--', label=f'Input Unity Gain Frequency: {unity_gain_freq_in:.2f} Hz')
    plt.axhline(-phase_margin_in, color='g', linestyle='--', label=f'Input Phase Margin: {phase_margin_in:.2f} degrees')
    plt.axvline(unity_gain_freq_out, color='b', linestyle='--', label=f'Output Unity Gain Frequency: {unity_gain_freq_out:.2f} Hz')
    plt.axhline(-phase_margin_out, color='m', linestyle='--', label=f'Output Phase Margin: {phase_margin_out:.2f} degrees')
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Magnitude [dB], Phase [degrees]')
    plt.title('Opamp Frequency Response')
    plt.legend()
    plt.grid(True)
    plt.show()
    