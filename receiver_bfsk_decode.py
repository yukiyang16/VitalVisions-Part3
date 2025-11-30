# receiver_bfsk_decode.py
# Decode BFSK alpha modulation from a recorded video.
# Requires: OpenCV, NumPy, SciPy (for windowing / FFT).

import cv2
import numpy as np
from scipy.signal import get_window
from numpy.fft import rfft, rfftfreq

########################
# User configuration
########################

# Path to the recorded video (from phone)
VIDEO_PATH = "recording_alpha_120cm.mp4"

# The bit string you transmitted in the sender
TRANSMITTED_BITS = "1011001110001111"  # MUST match the transmitter

BIT_DURATION = 0.4   # seconds per bit (same as transmitter)

# BFSK frequencies (Hz) must match transmitter settings
FREQ_0 = 5.0
FREQ_1 = 10.0

# FFT search band around each frequency (Hz)
FREQ_TOL = 1.0

# Region of interest (ROI) as fraction of frame:
# (center crop) [y0, y1, x0, x1] in 0–1
ROI_FRACTION = (0.3, 0.7, 0.3, 0.7)

########################
# Step 1: Read video and build intensity signal
########################

cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    raise RuntimeError(f"Could not open video: {VIDEO_PATH}")

fps = cap.get(cv2.CAP_PROP_FPS)
num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

print("Video FPS:", fps)
print("Total frames:", num_frames)

intensities = []

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Crop ROI (center region)
    h, w = gray.shape
    y0 = int(ROI_FRACTION[0] * h)
    y1 = int(ROI_FRACTION[1] * h)
    x0 = int(ROI_FRACTION[2] * w)
    x1 = int(ROI_FRACTION[3] * w)
    roi = gray[y0:y1, x0:x1]

    mean_intensity = roi.mean()
    intensities.append(mean_intensity)

cap.release()

intensities = np.array(intensities, dtype=np.float32)
N = len(intensities)
t = np.arange(N) / fps

print("Signal length (frames):", N)
print("Signal duration (seconds):", t[-1])

# Remove DC and normalize
signal = intensities - np.mean(intensities)
signal = signal / np.std(signal)

########################
# Step 2: Per-bit FFT classification (BFSK)
########################

num_bits = len(TRANSMITTED_BITS)
samples_per_bit = int(round(BIT_DURATION * fps))

print("Samples per bit:", samples_per_bit)

received_bits = []

# Precompute frequency axis for given window length
window = get_window("hann", samples_per_bit, fftbins=True)

for i in range(num_bits):
    start = i * samples_per_bit
    end = start + samples_per_bit
    if end > N:
        print("Warning: not enough frames for all bits, trimming.")
        break

    segment = signal[start:end] * window

    # Real FFT
    spectrum = np.abs(rfft(segment))
    freqs = rfftfreq(len(segment), d=1.0/fps)

    # Sum energy around FREQ_0 and FREQ_1
    idx0 = np.where((freqs >= FREQ_0 - FREQ_TOL) & (freqs <= FREQ_0 + FREQ_TOL))[0]
    idx1 = np.where((freqs >= FREQ_1 - FREQ_TOL) & (freqs <= FREQ_1 + FREQ_TOL))[0]

    energy0 = spectrum[idx0].sum()
    energy1 = spectrum[idx1].sum()

    bit_hat = '0' if energy0 >= energy1 else '1'
    received_bits.append(bit_hat)

received_bits_str = "".join(received_bits)
print("Transmitted bits:", TRANSMITTED_BITS)
print("Received bits   :", received_bits_str)

########################
# Step 3: BER and data rate
########################

min_len = min(len(TRANSMITTED_BITS), len(received_bits_str))
correct = sum(
    1 for i in range(min_len)
    if TRANSMITTED_BITS[i] == received_bits_str[i]
)

total_bits = min_len  # only compare overlapping part
ber = 1.0 - correct / total_bits

# Data rate = correctly received bits per second
# Total time used for these bits = total_bits * BIT_DURATION
data_rate = correct / (total_bits * BIT_DURATION)

print(f"Correct bits: {correct}/{total_bits}")
print(f"Bit error rate (BER): {ber:.4f}")
print(f"Data rate (bps): {data_rate:.2f}")