from xarm.wrapper import XArmAPI

class RoboticArm:
    def __init__(self, ip='192.168.1.111'):
        self.arm = XArmAPI(ip)
        self.arm.clean_warn()
        self.arm.clean_error()
        
        self.arm.motion_enable(True)
        self.arm.set_state(0)
        
        # Height for marker
        self.zLowered=135
        
        # Height for pen
        # self.zLowered=158
        
        self.zRaised=170
        self.roll=180
        self.pitch = 0
        self.yaw = 180
        self.speed=100
        
        self.min_x = 160  # 110 Maximum
        self.max_x = 375  

        self.min_y = -190
        self.max_y = 190
        
        
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
        Adjust the z height based on the (x,y) location when drawing.
        When not drawing, use the raised z height.
        """
        if draw:
            # Get region-specific correction.
            correction = self.get_z_correction(x, y)
            # Adjust the z value: if the mark is too light, we lower the pen (z becomes smaller),
            # if too deep, we raise the pen (z becomes larger).
            z = self.zLowered + correction
            self.arm.set_position(x, y, z, self.roll, self.pitch, self.yaw, speed=self.speed)
        else:
            self.arm.set_position(x, y, self.zRaised, self.roll, self.pitch, self.yaw, speed=self.speed)
            
    def reset_position(self):
        self.arm.set_position(-10, 150, self.zRaised, self.roll, self.pitch, self.yaw, speed=self.speed)


    def centre_position(self):
        self.arm.set_position(self.max_x - self.min_x, 0, self.zRaised, self.roll, self.pitch, self.yaw, speed=self.speed)
        
    def calibrate_corners(self):
        """
        Calibrate the arm to the center of the canvas.
        """
        self.arm.set_position(self.min_x, self.max_y, self.zRaised, self.roll, self.pitch, self.yaw, speed=self.speed)
        self.arm.set_position(self.min_x, self.max_y, self.zLowered, self.roll, self.pitch, self.yaw, speed=self.speed)
        self.arm.set_position(self.min_x, self.max_y, self.zRaised, self.roll, self.pitch, self.yaw, speed=self.speed)
        
        self.arm.set_position(self.min_x, self.min_y, self.zRaised, self.roll, self.pitch, self.yaw, speed=self.speed)
        self.arm.set_position(self.min_x, self.min_y, self.zLowered, self.roll, self.pitch, self.yaw, speed=self.speed)
        self.arm.set_position(self.min_x, self.min_y, self.zRaised, self.roll, self.pitch, self.yaw, speed=self.speed)

        self.arm.set_position(self.max_x, self.min_y, self.zRaised, self.roll, self.pitch, self.yaw, speed=self.speed)
        self.arm.set_position(self.max_x, self.min_y, self.zLowered, self.roll, self.pitch, self.yaw, speed=self.speed)
        self.arm.set_position(self.max_x, self.min_y, self.zRaised, self.roll, self.pitch, self.yaw, speed=self.speed)

        self.arm.set_position(self.max_x, self.max_y, self.zRaised, self.roll, self.pitch, self.yaw, speed=self.speed)
        self.arm.set_position(self.max_x, self.max_y, self.zLowered, self.roll, self.pitch, self.yaw, speed=self.speed)
        self.arm.set_position(self.max_x, self.max_y, self.zRaised, self.roll, self.pitch, self.yaw, speed=self.speed)
