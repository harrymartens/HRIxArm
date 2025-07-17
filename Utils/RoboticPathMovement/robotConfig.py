from xarm.wrapper import XArmAPI
import math

class RoboticArm:
    def __init__(self, ip='192.168.1.111', mode="marker"):
        self.arm = XArmAPI(ip)
        self.arm.clean_warn()
        self.arm.clean_error()
        
        self.arm.motion_enable(True)
        self.arm.set_state(0)
        
        if mode == "marker":
            # self.zLowered=135.5
            self.zLowered=126
        elif mode == "erase":
            self.zLowered=68
        else:
            self.zLowered=158
        
        # self.zRaised=170
        self.zRaised=131
        
        self.roll=180
        self.pitch = 0
        self.yaw = 0
        self.speed=200
        
        self.min_x = 160  # 110 Maximum
        self.max_x = 375  

        self.min_y = -190
        self.max_y = 190
        
    def change_mode(self, mode):
        if mode == "marker":
            # self.zLowered=135.5
            # self.zRaised=170
            self.zLowered=125.5
            self.zRaised=131

        elif mode == "erase":
            self.zLowered=68
            self.zRaised=80
            
        else:
            self.zLowered=158
            self.zRaised=170
            
    def change_attachment_position(self):
        self.centre_position()
        self.arm.set_position(200, 0, 200,
                                    self.roll, self.pitch, self.yaw,
                                    speed=100, mvacc=100)
        self.arm.set_position(200, 0, 200,
                                    90, self.pitch, self.yaw,
                                    speed=100, mvacc=100)
        
            
            
    def subdivide_line(self, p1, p2, max_step=0.05):
        """
        Break the line from p1=(x,y,z) to p2 into segments ≤ max_step length.
        Returns list of intermediate points excluding p1.
        """
        dx, dy, dz = p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist <= max_step:
            return [p2]
        steps = math.ceil(dist / max_step)
        return [
            (
                p1[0] + dx * i/steps,
                p1[1] + dy * i/steps,
                p1[2] + dz * i/steps
            ) for i in range(1, steps + 1)
        ]

        
        
    def get_dimensions(self):
        return (self.max_x - self.min_x, self.max_y - self.min_y)
        
    def get_z_correction(self, x, y):
        """
        Determine a z correction based on the (x,y) region of the canvas.
        We assume a grid of 7 columns (0 to 6) and 5 rows (0 to 4), where row 0 is the bottom.
        Corrections are determined by calibration:
        - For a mark that is too light, lower the pen by 0.1.
        - For a mark that is too deep, raise the pen by 0.1.
        - For marks that "cannot be seen", lower the pen by 0.2.
        """
        # Determine grid indices from x and y.
        # Make sure self.min_x, self.max_x, self.min_y, self.max_y are defined in your class.
        num_columns = 5
        num_rows = 5
        # Normalize x and y to a 0-(num_columns-1) or 0-(num_rows-1) range.
        row = int(round((x - self.min_x) / (self.max_x - self.min_x) * (num_rows - 1)))
        col = int(round((y - self.min_y) / (self.max_y - self.min_y) * (num_columns - 1)))
        # Initialize correction.
        correction = 0.0

        # Calibration feedback from each row.
        if row == 0:
            if col in [0]:
                correction = -0.2
            elif col in [1]:
                correction = -0.1
            elif col in [2]:
                correction = -0.1
            elif col in [3]:
                correction = 0.1
            elif col in [4]:
                correction = 0.1
        elif row == 1:
            if col in [0]:
                correction = -0.3
            elif col in [1]:
                correction = -0.3
            elif col in [2]:
                correction = -0.3
            elif col in [3]:
                correction = 0.1
            elif col in [4]:
                correction = 0.2
        elif row == 2:
            if col in [0]:
                correction = -0.5
            elif col in [1]:
                correction = -0.5
            elif col in [2]:
                correction = -0.3
            elif col in [3]:
                correction = -0.2
            elif col in [4]:
                correction = 0
        elif row == 3:
            if col in [0]:
                correction = -0.5
            elif col in [1]:
                correction = -0.5
            elif col in [2]:
                correction = -0.4
            elif col in [3]:
                correction = -0.4
            elif col in [4]:
                correction = -0.3
        elif row == 4:
            if col in [0]:
                correction = -0.7
            elif col in [1]:
                correction = -0.6
            elif col in [2]:
                correction = -0.2
            elif col in [3]:
                correction = -0.3
            elif col in [4]:
                correction = -0.4

        return correction
    
    def set_position(self, x, y, draw):
        """
        Adjust z for draw or raised. Perform direct Cartesian move first;
        on singularity (error code 24), subdivide path and retry each chunk,
        falling back to joint-space for repeating singularities.
        """
        # Determine target z
        if draw:
            correction = self.get_z_correction(x, y)
            z = self.zLowered + correction
        else:
            z = self.zRaised

        # Attempt direct Cartesian move
        ret = self.arm.set_position(x, y, z,
                                    self.roll, self.pitch, self.yaw,
                                    speed=self.speed, mvacc=100)
        
        print("RET: ",ret)
        
        if ret == 0:
            return ret
        else:
            if self.arm.error_code != 24:
                print(f"[ERROR] set_position failed, code: {ret}")
                print(f"Error code: {self.arm.error_code}, Warning code: {self.arm.warn_code}")
                return ret

        print("A SINGULARITY HAS OCCURED - RETRYING")

        # Singularity encountered: subdivide path
        current = self.arm.get_position()  # returns (x0,y0,z0,roll,pitch,yaw)
        waypoints = self.subdivide_line(current[:3], (x, y, z))

        # 3) Iterate waypoints
        for wx, wy, wz in waypoints:
            ret_wp = self.arm.set_position(
                wx, wy, wz,
                self.roll, self.pitch, self.yaw,
                speed=self.speed, mvacc=100
            )
            if ret_wp == 24:
                # still singular: compute IK and move via servo angles
                pose = [wx, wy, wz, self.roll, self.pitch, self.yaw]
                code, joints = self.arm.get_inverse_kinematics(
                    pose,
                    input_is_radian=False,
                    return_is_radian=True
                )
                if code != 0:
                    print(f"[ERROR] IK failed at ({wx:.3f},{wy:.3f},{wz:.3f}), code={code}")
                    return code
                ret_wp = self.arm.set_servo_angle(
                    angle=joints,
                    is_radian=True,
                    speed=self.speed,
                    mvacc=100,
                    wait=False
                )
            if ret_wp not in (0, 24):
                print(f"[ERROR] waypoint move to ({wx:.3f},{wy:.3f},{wz:.3f}) failed, code={ret_wp}")
                return ret_wp

        # All waypoints succeeded
        return 0

            
    def reset_position(self):
        self.arm.set_position(-10, 150, self.zRaised, self.roll, self.pitch, self.yaw, speed=50, mvacc=50)

    def centre_position(self):
        self.arm.set_position(self.max_x - self.min_x, 0, self.zRaised, self.roll, self.pitch, self.yaw, speed=50, mvacc=50)
        
    def calibrate_corners(self):
        """
        Calibrate the arm to the center of the canvas.
        """
        self.arm.set_position(self.min_x, self.max_y, self.zRaised, self.roll, self.pitch, self.yaw, speed=self.speed, mvacc=100)
        self.arm.set_position(self.min_x, self.max_y, self.zLowered, self.roll, self.pitch, self.yaw, speed=self.speed, mvacc=100)
        self.arm.set_position(self.min_x, self.max_y, self.zRaised, self.roll, self.pitch, self.yaw, speed=self.speed, mvacc=100)
        
        self.arm.set_position(self.min_x, self.min_y, self.zRaised, self.roll, self.pitch, self.yaw, speed=self.speed, mvacc=100)
        self.arm.set_position(self.min_x, self.min_y, self.zLowered, self.roll, self.pitch, self.yaw, speed=self.speed, mvacc=100)
        self.arm.set_position(self.min_x, self.min_y, self.zRaised, self.roll, self.pitch, self.yaw, speed=self.speed, mvacc=100)

        self.arm.set_position(self.max_x, self.min_y, self.zRaised, self.roll, self.pitch, self.yaw, speed=self.speed, mvacc=100)
        self.arm.set_position(self.max_x, self.min_y, self.zLowered, self.roll, self.pitch, self.yaw, speed=self.speed, mvacc=100)
        self.arm.set_position(self.max_x, self.min_y, self.zRaised, self.roll, self.pitch, self.yaw, speed=self.speed, mvacc=100)

        self.arm.set_position(self.max_x, self.max_y, self.zRaised, self.roll, self.pitch, self.yaw, speed=self.speed, mvacc=100)
        self.arm.set_position(self.max_x, self.max_y, self.zLowered, self.roll, self.pitch, self.yaw, speed=self.speed, mvacc=100)
        self.arm.set_position(self.max_x, self.max_y, self.zRaised, self.roll, self.pitch, self.yaw, speed=self.speed, mvacc=100)
