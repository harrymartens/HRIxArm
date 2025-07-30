#!/usr/bin/env python3

import pygame
import time
import math
from xarm.wrapper import XArmAPI

# Robot connection setup
ROBOT_IP = "192.168.1.111"
arm = XArmAPI(ROBOT_IP)
arm.motion_enable(True)
arm.set_collision_sensitivity(2)    # Lower sensitivity to reduce false positives
arm.set_mode(0)                     # Position control mode
arm.set_state(0)                    # Ready state
arm.move_gohome(wait=True)
arm.set_position(171, 0, 156, 180, 0, 0, wait=True, speed=100)

# Switch to Cartesian servo mode
arm.set_mode(1)
arm.set_state(0)
time.sleep(0.1)

# Movement bounds
BOUND_X_MIN, BOUND_X_MAX = 175, 330
BOUND_Y_MIN, BOUND_Y_MAX = -285, 285
BOUND_Z_MIN, BOUND_Z_MAX = 136, 400
PITCH_MIN, PITCH_MAX = -90, 90

# Sensitivity
SPEED_XY = 1.0    # mm per loop
SPEED_Z = 1.0     # mm per loop
PITCH_STEP = 2.0  # degrees per press
DEADZONE = 0.1

# Initial pose and orientation
pose = {"x": 171.0, "y": 0.0, "z": 156.0}
orientation = {"roll": 180.0, "pitch": 0.0, "yaw": 0.0}

# Initialise controller
pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

def clamp(val, min_val, max_val):
    return max(min(val, max_val), min_val)

def apply_deadzone(val):
    return 0.0 if abs(val) < DEADZONE else val

def update_pose():
    # Read axes/buttons
    x_axis = apply_deadzone(joystick.get_axis(0))
    y_axis = apply_deadzone(joystick.get_axis(1))
    z_up    = joystick.get_button(2)
    z_down  = joystick.get_button(0)
    pitch_up   = joystick.get_button(1)
    pitch_down = joystick.get_button(3)
    roll_up    = joystick.get_button(9)
    roll_down  = joystick.get_button(10)

    # Compute deltas
    dx = x_axis * SPEED_XY
    dy = -y_axis * SPEED_XY
    dz =  SPEED_Z if z_up else -SPEED_Z if z_down else 0.0
    dp =  PITCH_STEP if pitch_up else -PITCH_STEP if pitch_down else 0.0
    dr =  PITCH_STEP if roll_up   else -PITCH_STEP if roll_down else 0.0

    # Apply and clamp
    pose["x"]     = clamp(pose["x"]     + dx, BOUND_X_MIN, BOUND_X_MAX)
    pose["y"]     = clamp(pose["y"]     + dy, BOUND_Y_MIN, BOUND_Y_MAX)
    pose["z"]     = clamp(pose["z"]     + dz, BOUND_Z_MIN, BOUND_Z_MAX)
    orientation["pitch"] = clamp(orientation["pitch"] + dp, PITCH_MIN, PITCH_MAX)
    orientation["roll"]  = (orientation["roll"]  + dr) % 360

def main():
    print("Control the robot with the PS4 controller. Press CTRL+C to exit.")

    prev_mvpose = [
        pose["x"], pose["y"], pose["z"],
        orientation["roll"], orientation["pitch"], orientation["yaw"]
    ]

    try:
        while True:
            pygame.event.pump()
            update_pose()

            mvpose = [
                pose["x"], pose["y"], pose["z"],
                orientation["roll"], orientation["pitch"], orientation["yaw"]
            ]

            ret = arm.set_servo_cartesian(mvpose, speed=50, mvacc=50)
            print(f"set_servo_cartesian mvpose={mvpose}, ret={ret}")

            if ret == 0:
                # Successful move; record as last good pose
                prev_mvpose = mvpose.copy()

            else:
                break

            time.sleep(0.01)  # 100 Hz control loop

    except KeyboardInterrupt:
        print("\nExiting and shutting down controller…")
    finally:
        pygame.quit()
        arm.disconnect()

if __name__ == "__main__":
    main()