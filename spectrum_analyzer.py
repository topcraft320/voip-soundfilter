#!/usr/bin/env python3
"""Plot the live microphone signal(s) RFFT with matplotlib.

Matplotlib and NumPy have to be installed.

"""
import argparse
import queue
import sys
import math


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-l', '--list-devices', action='store_true', help='show list of audio devices and exit')
parser.add_argument('-d', '--device', type=int_or_str, help='input device (numeric ID or substring)')
parser.add_argument('-b', '--block-duration', type=float, metavar='DURATION', default=50, help='block size (default %(default)s milliseconds)')
parser.add_argument('-c', '--channel', type=int, default=0, help='channel used for spectrum analysis (default 0)')
parser.add_argument('-i', '--interval', type=float, default=30, help='minimum time between plot updates (default: %(default)s ms)')
args = parser.parse_args()

if args.channel < 0:
    parser.error('Channel must be greater than 0')

q = queue.Queue()

def audio_callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status)
    if not q.full():
        q.put(indata[:, args.channel])

def update_plot(frame):
    """This is called by matplotlib for each plot update.

    Typically, audio callbacks happen more frequently than plot updates,
    therefore the queue tends to contain multiple blocks of audio data.

    """
    global plotdata
    try:
        data = q.get()
        plotdata = np.abs(np.fft.rfft(data))
        plotdata = plotdata/np.linalg.norm(plotdata)
        for line in lines:
            line.set_ydata(plotdata)
        return lines
    except queue.Empty:
        return lines

try:
    from matplotlib.animation import FuncAnimation
    import matplotlib.pyplot as plt
    import numpy as np
    import sounddevice as sd

    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)
    
    device_info = sd.query_devices(args.device, 'input')
    samplerate = device_info['default_samplerate']
    print('Using device:', args.device, device_info)

    fftlen = math.ceil(samplerate * args.block_duration / 1000)

    if fftlen % 2 == 0:
        length = int((fftlen / 2) + 1)
    else:
        length = int((fftlen + 1) / 2)
    print('Plotting with:', length, 'points of data corresponding to a range of:', samplerate/length, 'Hz per point of data.')

    plotdata = np.zeros(length)

    fig, ax = plt.subplots()
    lines = ax.plot(plotdata)
    ax.axis((0, len(plotdata), 0, 1))
    ax.set_yticks([0])
    ax.yaxis.grid(True)
    ax.tick_params(bottom=False, top=False, labelbottom=False, right=False, left=False, labelleft=False)
    fig.tight_layout(pad=0)

    stream = sd.InputStream(device=args.device, blocksize=int(samplerate * args.block_duration / 1000),
        samplerate=samplerate, callback=audio_callback)

    ani = FuncAnimation(fig, update_plot, interval=args.interval, blit=True)
    with stream:
        plt.show()

except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))