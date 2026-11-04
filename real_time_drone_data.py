class RealTimeDroneData:
    def __init__(
        self,
        timestamp,
        x_angular_speed,
        y_angular_speed,
        z_angular_speed,
        x_accel,
        y_accel,
        z_accel,
        height,
        yaw_angle,
        pressure,
        front_range,
        x_flow,
        y_flow,
        color_data,
        x_position,
        y_position,
        z_position,
        speed_mps,
    ):
        self.timestamp = timestamp

        # gyroscope
        self.x_angular_speed = x_angular_speed
        self.y_angular_speed = y_angular_speed
        self.z_angular_speed = z_angular_speed
        self.yaw_angle = yaw_angle

        # accelerometer
        self.x_accel = x_accel
        self.y_accel = y_accel
        self.z_accel = z_accel

        # bottom range sensor
        self.height = height

        # barometer
        self.pressure = pressure

        # front range sensor
        self.front_range = front_range

        # optical flow sensor
        self.x_flow = x_flow
        self.y_flow = y_flow

        # color sensors
        self.color_data = color_data

        # position in meters and estimated speed in m/s
        self.x_position = x_position
        self.y_position = y_position
        self.z_position = z_position
        self.speed_mps = speed_mps

    def __repr__(self):
        return (
            f"timestamp: {self.timestamp}, "
            f"x_angular_speed: {self.x_angular_speed}, "
            f"y_angular_speed: {self.y_angular_speed}, "
            f"z_angular_speed: {self.z_angular_speed}, "
            f"x_accel: {self.x_accel}, "
            f"y_accel: {self.y_accel}, "
            f"z_accel: {self.z_accel}, "
            f"height: {self.height}, "
            f"yaw_angle: {self.yaw_angle}, "
            f"pressure: {self.pressure}, "
            f"front_range: {self.front_range}, "
            f"x_flow: {self.x_flow}, "
            f"y_flow: {self.y_flow}, "
            f"color_data: {self.color_data}, "
            f"x_position: {self.x_position}, "
            f"y_position: {self.y_position}, "
            f"z_position: {self.z_position}, "
            f"speed_mps: {self.speed_mps}"
        )
