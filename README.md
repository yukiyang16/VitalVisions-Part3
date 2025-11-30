# Vital Visions - Part 3: BFSK Alpha-channel Communication

This repository contains the code for the screen-to-camera communication system
implemented for Part 3 of HW4 in 17-720 (Machine Learning and Sensing for Healthcare).

## Files
- `transmitter_bfsk_alpha.py`: Generates BFSK alpha modulation on a static image.
- `receiver_bfsk_decode.py`: Decodes BFSK bits from recorded smartphone video.
- `sample_bitstrings/`: optional folder for test sequences.

## How to use
1. Run transmitter script on a laptop display.
2. Record with smartphone camera at different distances.
3. Run receiver script to extract bits, compute BER and data rate.
