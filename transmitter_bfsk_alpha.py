# transmitter_bfsk_alpha.py
# Simple BFSK transmitter using alpha modulation on top of a static background.
# Display this full-screen on a monitor; record it using a phone camera.

import pygame
import time
import math
import sys

########################
# User configuration
########################

# Bit sequence to transmit (you can change per experiment)
BIT_STRING = "1011001110001111"   # example, 16 bits

BIT_DURATION = 0.4   # seconds per bit  (e.g., 0.4 s -> 2.5 bits/sec)

# BFSK frequencies (Hz) for bit 0 and bit 1
FREQ_0 = 5.0         # low frequency for bit '0'
FREQ_1 = 10.0        # high frequency for bit '1'

# Base alpha and delta alpha (normalized 0–1)
BASE_ALPHA = 0.5     # constant background translucency
DELTA_ALPHA = 0.1    # change this to 0.1 or 0.5 for your experiments

# Screen size (you can set to your monitor resolution)
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Background color (R,G,B) — you can also load an image instead
BG_COLOR = (50, 80, 120)  # dark blue-gray

# Rect overlay color (white)
OVERLAY_COLOR = (255, 255, 255)

########################
# Helper functions
########################

def get_current_bit(t, bit_duration, bit_string):
    """
    Given the elapsed time t (seconds), return:
      - current bit index (0-based)
      - bit value ('0' or '1')
    If t exceeds the last bit, return (None, None).
    """
    bit_index = int(t // bit_duration)
    if bit_index < len(bit_string):
        return bit_index, bit_string[bit_index]
    else:
        return None, None


def compute_alpha(t_local, bit_value):
    """
    Compute the normalized alpha (0–1) at time t_local
    within the current bit interval, using BFSK.
    BASE_ALPHA is the DC level, DELTA_ALPHA is modulation amplitude.
    """
    if bit_value == '0':
        freq = FREQ_0
    else:
        freq = FREQ_1

    # Simple sinusoidal modulation
    alpha_norm = BASE_ALPHA + DELTA_ALPHA * math.sin(2 * math.pi * freq * t_local)

    # Clamp to [0, 1]
    alpha_norm = max(0.0, min(1.0, alpha_norm))
    return alpha_norm

########################
# Main
########################

def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("BFSK Alpha Transmitter")

    clock = pygame.time.Clock()

    # Create overlay surface with per-pixel alpha enabled
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    start_time = time.time()
    running = True

    print("Transmitting bit string:", BIT_STRING)
    print("Bit duration:", BIT_DURATION, "s")
    print("FREQ_0 (bit 0):", FREQ_0, "Hz")
    print("FREQ_1 (bit 1):", FREQ_1, "Hz")
    print("DELTA_ALPHA (normalized):", DELTA_ALPHA)

    while running:
        # Handle events (close window)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Elapsed time since start (seconds)
        t = time.time() - start_time

        # Determine current bit
        bit_index, bit_value = get_current_bit(t, BIT_DURATION, BIT_STRING)

        # Stop after all bits are sent
        if bit_index is None:
            print("Transmission finished.")
            running = False
        else:
            # Time within the current bit interval
            t_local = t - bit_index * BIT_DURATION

            # Compute alpha
            alpha_norm = compute_alpha(t_local, bit_value)
            alpha_255 = int(alpha_norm * 255)

            # Fill background
            screen.fill(BG_COLOR)

            # Draw white overlay with computed alpha
            overlay.fill((OVERLAY_COLOR[0], OVERLAY_COLOR[1], OVERLAY_COLOR[2], alpha_255))
            screen.blit(overlay, (0, 0))

            # Optionally display text (bit index, bit value)
            font = pygame.font.SysFont(None, 40)
            text_surface = font.render(f"Bit {bit_index+1}/{len(BIT_STRING)}: {bit_value}", True, (255, 255, 255))
            screen.blit(text_surface, (20, 20))

            pygame.display.flip()
            clock.tick(60)  # try to keep ~60 FPS

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()