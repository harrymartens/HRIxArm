#!/usr/bin/env python3
import time
import math
import pygame
from xarm.wrapper import XArmAPI

# ====== Robot & Control Defaults (from the "better" fightstick script) ======
ROBOT_IP = "192.168.1.111"

# Movement bounds
BOUND_X_MIN, BOUND_X_MAX = 175, 330
BOUND_Y_MIN, BOUND_Y_MAX = -285, 285
BOUND_Z_MIN, BOUND_Z_MAX = 158, 400
PITCH_MIN, PITCH_MAX = -90, 90

# Sensitivity
SPEED_XY = 1.0      # mm per loop
SPEED_Z = 1.0       # mm per loop
PITCH_STEP = 1.0    # degrees per step/loop
DEADZONE = 0.1

# Initial pose/orientation (fightstick starting pose kept)
INIT_POSE = {"x": 200.0, "y": 0.0, "z": 200.0}
INIT_ORI  = {"roll": 180.0, "pitch": 0.0, "yaw": 0.0}

# ====== Helpers ======
def clamp(val, lo, hi):
    return max(lo, min(hi, val))

def apply_deadzone(v, dz=DEADZONE):
    return 0.0 if abs(v) < dz else v

def connect_robot():
    arm = XArmAPI(ROBOT_IP)
    arm.motion_enable(True)
    arm.set_collision_sensitivity(5)     # reduce false positives
    arm.set_mode(0)                      # Position mode
    arm.set_state(0)
    # Safe ready pose
    arm.set_position(200, 0, 200, 180, 0, 0, speed=5, wait=True)
    # Switch to Cartesian servo mode
    arm.set_mode(1)
    arm.set_state(0)
    time.sleep(0.1)
    return arm

def init_joystick():
    pygame.init()
    pygame.joystick.init()
    if pygame.joystick.get_count() == 0:
        raise RuntimeError("No joystick detected. Plug in a controller and try again.")
    js = pygame.joystick.Joystick(0)
    js.init()
    return js

# ====== Controller Profiles ======
class BaseProfile:
    name = "base"
    def help(self):
        pass
    def read_deltas(self, js):
        """Return dx, dy, dz, dpitch, droll per control tick."""
        return 0.0, 0.0, 0.0, 0.0, 0.0

class FightstickProfile(BaseProfile):
    """
    Mapping per original fightstick.py:
      - Left stick X/Y: axes 0/1 -> X/Y motion
      - Z up/down: buttons 2 / 0
      - Pitch up/down: buttons 1 / 3
      - Roll up/down: buttons 9 / 10
    """
    name = "fightstick"
    def help(self):
        print(
            "Controls (fightstick):\n"
            "  Left stick: X/Y move\n"
            "  Button 2 = Z+, Button 0 = Z-\n"
            "  Button 1 = Pitch+, Button 3 = Pitch-\n"
            "  Button 9 = Roll+,  Button 10 = Roll-\n"
            "  Ctrl+C to exit."
        )

    def read_deltas(self, js):
        x_axis = apply_deadzone(js.get_axis(0))
        y_axis = apply_deadzone(js.get_axis(1))
        z_up    = js.get_button(2)
        z_down  = js.get_button(0)
        pitch_up   = js.get_button(1)
        pitch_down = js.get_button(3)
        roll_up    = js.get_button(9)
        roll_down  = js.get_button(10)

        dx = x_axis * SPEED_XY
        dy = -y_axis * SPEED_XY
        dz = (SPEED_Z if z_up else 0.0) - (SPEED_Z if z_down else 0.0)
        dp = (PITCH_STEP if pitch_up else 0.0) - (PITCH_STEP if pitch_down else 0.0)
        dr = (PITCH_STEP if roll_up  else 0.0) - (PITCH_STEP if roll_down else 0.0)
        return dx, dy, dz, dp, dr

class PS4Profile(BaseProfile):
    """
    Mapping from controller.py (PS4/DualShock-style):
      - Left stick X/Y: axes 0/1 -> X/Y motion
      - Triggers L2/R2: axes 4/5 in [-1..1], map to [0..1], Z via (L2 - R2)
      - Right stick Y: axis 3 -> pitch (down increases pitch)
      - No roll mapped here (can add shoulders if needed)
    """
    name = "ps4"
    def help(self):
        print(
            "Controls (PS4):\n"
            "  Left stick: X/Y move\n"
            "  L2/R2: Z up/down\n"
            "  Right stick Y: Pitch (down = pitch+)\n"
            "  Ctrl+C to exit."
        )

    def read_deltas(self, js):
        left_x  = apply_deadzone(js.get_axis(0))
        left_y  = apply_deadzone(js.get_axis(1))
        right_y = apply_deadzone(js.get_axis(3))
        # Triggers come as [-1..1]; map to [0..1]
        l2 = (js.get_axis(4) + 1) / 2
        r2 = (js.get_axis(5) + 1) / 2

        dx = left_x * SPEED_XY
        dy = -left_y * SPEED_XY
        dz = (l2 - r2) * SPEED_Z
        dp = -right_y * PITCH_STEP
        dr = 0.0
        return dx, dy, dz, dp, dr

# Profile registry
PROFILES = {
    "fightstick": FightstickProfile(),
    "ps4": PS4Profile(),
}

def pick_profile():
    choice = input("Controller type [fightstick/ps4]: ").strip().lower()
    if choice not in PROFILES:
        print(f"Unknown controller '{choice}'. Defaulting to 'fightstick'.")
        choice = "fightstick"
    return PROFILES[choice]

def main():
    profile = pick_profile()
    arm = None
    try:
        arm = connect_robot()
        js = init_joystick()
        profile.help()

        pose = dict(INIT_POSE)
        orientation = dict(INIT_ORI)

        prev_mvpose = [
            pose["x"], pose["y"], pose["z"],
            orientation["roll"], orientation["pitch"], orientation["yaw"]
        ]

        print("Entering control loop. Ctrl+C to exit.")
        while True:
            pygame.event.pump()

            dx, dy, dz, dp, dr = profile.read_deltas(js)

            # Integrate & clamp
            pose["x"] = clamp(pose["x"] + dx, BOUND_X_MIN, BOUND_X_MAX)
            pose["y"] = clamp(pose["y"] + dy, BOUND_Y_MIN, BOUND_Y_MAX)
            pose["z"] = clamp(pose["z"] + dz, BOUND_Z_MIN, BOUND_Z_MAX)
            orientation["pitch"] = clamp(orientation["pitch"] + dp, PITCH_MIN, PITCH_MAX)
            orientation["roll"]  = (orientation["roll"] + dr) % 360.0

            mvpose = [
                pose["x"], pose["y"], pose["z"],
                orientation["roll"], orientation["pitch"], orientation["yaw"]
            ]

            ret = arm.set_servo_cartesian(mvpose, speed=50, mvacc=50)
            print(f"set_servo_cartesian mvpose={mvpose}, ret={ret}")

            if ret == 0:
                prev_mvpose = mvpose.copy()
            else:
                # Non-zero return typically indicates an error (e.g., collision)
                # Break so operator can address it (or you can add recovery logic here)
                print("Non-zero return from set_servo_cartesian; stopping loop.")
                break

            time.sleep(0.01)  # ~100 Hz

    except KeyboardInterrupt:
        print("\nExiting…")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        try:
            pygame.quit()
        except Exception:
            pass
        if arm is not None:
            try:
                arm.disconnect()
            except Exception:
                pass

if __name__ == "__main__":
    main()