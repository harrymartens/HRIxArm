#!/usr/bin/env python3

import pygame
import time

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No controller detected.")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()

print(f"Controller name: {joystick.get_name()}")
print(f"Number of axes: {joystick.get_numaxes()}")
print(f"Number of buttons: {joystick.get_numbuttons()}")
print(f"Number of hats: {joystick.get_numhats()}\n")

try:
    while True:
        pygame.event.pump()

        # Axes (analog sticks, triggers)
        axes = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
        print("Axes:")
        for i, val in enumerate(axes):
            print(f"  Axis {i}: {val:.2f}")

        # Buttons (X, O, square, triangle, L1, R1, etc.)
        print("Buttons:")
        for i in range(joystick.get_numbuttons()):
            pressed = joystick.get_button(i)
            print(f"  Button {i}: {'Pressed' if pressed else 'Released'}")

        # D-pad (hat) values
        print("D-Pad:")
        for i in range(joystick.get_numhats()):
            hat = joystick.get_hat(i)
            print(f"  Hat {i}: {hat}")

        print("-" * 40)
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nExiting...")
finally:
    pygame.quit()