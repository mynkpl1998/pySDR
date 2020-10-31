import signal
import argparse
import numpy as np
from collections import deque
from pysdr.rtlsdr import Radio
import matplotlib.pyplot as plt
plt.style.use(['fast'])
from pysdr.utils import print_info_msg
from pysdr.rtlsdr_apis import librtlsdr
import matplotlib.animation as animation

parser = argparse.ArgumentParser(description="Spectrum analyzer tool for pysdr.")
parser.add_argument("-f", "--center-freq", type=int, default=980e6, help="Center frequency in Hz. Default: 980 MHz.")
parser.add_argument("-s", "--sample-rate", type=int, default=1e6, help="Sample rate per second. Default: 1 MSPS.")
parser.add_argument("-agc", "--enable-agc", type=int, default=1, help="Enable AGC of the RTL32832. 1-Enable, 0-Disbale. Default: Enabled.")
parser.add_argument("-auto-gain", "--enable-auto-tuner-gain", default=1, type=int, help="Enable tuner auto gain selection. Default: Enabled.")
parser.add_argument("-g", "--gain", type=float, default=0.0, help="Tuner gain in dB. Default: 0 dB.")
parser.add_argument("-n", "--samples", type=int, default=1024, help="Number of samples to use for calculating FFT. Default: 1024.")
parser.add_argument("-qg", "--query-gains", default=0, type=int, help="Query supported tuner gain values. Default: 0.")
parser.add_argument("-qd", "--query-device", default=0, type=int, help="Query number of supported RTL-SDR(s) to the host. Default: 0.")
parser.add_argument("-d", "--device-index", required=True, type=int, help="Device index.")
parser.add_argument("-l", "--logging-level", default=3, type=int, help="Logging level, (1-4). Default: 3")
parser.add_argument("-p", "--ppm", type=int, default=0, help="Freq offset correction value in ppm. Default: 0 ppm. (No correction).")
parser.add_argument("-mp", "--plot-mag-pha", type=int, default=0, help="Enable plot of mag and phase of the signal. Default: 0. Disabled.")

args = parser.parse_args()

max_frames = 300
frame_count = 0
waterfall_queue = deque(maxlen=max_frames)
for idx in range(max_frames):
    waterfall_queue.append(np.zeros(args.samples))

def plot_samples(i, sdr, axes):
    """
    This function plots the FFT and PSD of the
    samples received from the RTL-SDR.

    Parameters
    ----------
    * i                            : (int) For matplotlib internal use.
    * sdr                          : (pysdr.rtlsdr.Radio) The SDR Radio object.
    * axes                         : (matplotlib.subplots) Axis to plot graphs.
    """
    
    # Plot FFT
    num_sample_pts = sdr.num_recv_samples
    samples = sdr.rx_samples()
    signal_fft = np.fft.fftshift(np.fft.fft(samples))
    #signal_fft = signal_fft * np.hamming(signal_fft.size)
    signal_mag = np.abs(signal_fft)
    signal_pha = np.angle(signal_fft)
    signal_psd = np.abs(signal_fft/sdr.sample_rate)**2
    signal_psd_db = 10.0 * np.log10(signal_psd)

    fft_resolution = int(sdr.sample_rate/num_sample_pts)
    low_freq = sdr.center_freq - sdr.sample_rate/2
    high_freq = sdr.center_freq + sdr.sample_rate/2
    freq = np.arange(low_freq, high_freq, fft_resolution)[0:num_sample_pts]
    
    waterfall_queue.append(signal_mag)
    axis_dict['wfall-axis']['axis'].clear()
    axis_dict['wfall-axis']['axis'].imshow(waterfall_queue, cmap='YlOrBr', interpolation='bicubic', aspect='auto')
    axis_dict['wfall-axis']['axis'].xaxis.set_ticklabels([])
    axis_dict['wfall-axis']['axis'].set_ylabel("Time")
    
    if args.plot_mag_pha == 1:
        axis_dict['mag-axis']['axis'].clear()
        axis_dict['mag-axis']['axis'].set_ylabel("Magnitude")
        axis_dict['mag-axis']['axis'].plot(freq/1e6, signal_mag, linewidth=0.5)
        axis_dict['mag-axis']['axis'].set_ylim([-5, 350])
        axis_dict['mag-axis']['axis'].grid()

    if args.plot_mag_pha == 1:
        axis_dict['pha-axis']['axis'].clear()
        axis_dict['pha-axis']['axis'].set_ylabel("Phase")
        axis_dict['pha-axis']['axis'].plot(freq/1e6, signal_pha, linewidth=0.5)
        axis_dict['pha-axis']['axis'].set_ylim([-7, 7])
        axis_dict['pha-axis']['axis'].grid()
        
    axis_dict['psd-axis']['axis'].clear()
    axis_dict['psd-axis']['axis'].set_xlabel("Frequency (MHz)")
    axis_dict['psd-axis']['axis'].set_ylabel("PSD (dB)")
    axis_dict['psd-axis']['axis'].plot(freq/1e6, signal_psd_db, linewidth=0.5)
    axis_dict['psd-axis']['axis'].set_ylim([-135, -20])
    axis_dict['psd-axis']['axis'].grid()
    
    
   
def signal_handler(sdr):
    """
    Used to handle SIGINT.
    """
    print_info_msg("Caught Ctrl-C. Clearing resources. Exiting.")
    sdr.close()
    exit(0)

if __name__ == "__main__":

    # Create an object of the librtlsdr
    lrtlsdr = librtlsdr()
    
    if args.query_device == 1:
        attached_devices = lrtlsdr.py_rtlsdr_get_device_count()
        print_info_msg("Number of RTL-SDR device(s) attached to the host: %d"%(attached_devices))
        exit(0)

    sdr = Radio(device_index=args.device_index, logging_level=args.logging_level)
    
    # Check if querying for supported lna gain values.
    if args.query_gains == 1:
        print_info_msg("Supported Tuner/LNA gain values in dB: %s"%(sdr.tuner_gains))
        exit(0)
    
    # set the radio properties
    sdr.center_freq = args.center_freq
    sdr.sample_rate = args.sample_rate
    if args.enable_agc == 1:
        sdr.enable_agc = True
    else:
        sdr.enable_agc = False
    if args.enable_auto_tuner_gain == 1:
        sdr.enable_auto_tuner_gain = True
    else:
        sdr.tuner_gain = args.gain
    sdr.num_recv_samples = args.samples

    if args.ppm != 0:
        sdr.freq_correction = args.ppm
    
    # Print device settings
    sdr.print_device_configuration()

    # Plot axes.
    fig = plt.figure()

    if args.plot_mag_pha == 1:
        waterfall_axis = fig.add_subplot(2, 2, 3)
        psd_axis = fig.add_subplot(2, 2, 1)
        mag_axis = fig.add_subplot(2, 2, 2)
        pha_axis = fig.add_subplot(2, 2, 4)

    else:
        waterfall_axis = fig.add_subplot(2, 1, 2)
        psd_axis = fig.add_subplot(2, 1, 1)
    
    if args.plot_mag_pha == 1:
        axis_dict = {'wfall-axis': {'axis': waterfall_axis,
                                'ylim': [float('inf'), -float('inf')] },
                    'psd-axis': {'axis': psd_axis},
                    'mag-axis': {'axis': mag_axis},
                    'pha-axis': {'axis': pha_axis}}
    else:
        axis_dict = {'wfall-axis': {'axis': waterfall_axis,
                                'ylim': [float('inf'), -float('inf')] },
                    'psd-axis': {'axis': psd_axis}}
    
    ani = animation.FuncAnimation(fig, plot_samples, fargs=(sdr, axis_dict,), interval=10)
    plt.show