from real_time_drone_data import RealTimeDroneData
from main import save_to_csv
from main import save_to_csv, upload_to_s3

sample = RealTimeDroneData(
    timestamp=1,
    x_angular_speed=0,
    y_angular_speed=0,
    z_angular_speed=0,
    x_accel=0,
    y_accel=0,
    z_accel=9.8,
    height=0,
    yaw_angle=0,
    pressure=101325,
    front_range=1,
    x_flow=0,
    y_flow=0,
    color_data=[100, 50, 25],
    x_position=0,
    y_position=0,
    z_position=0,
    speed_mps=0
)

print(sample)
save_to_csv([sample], "flight_data.csv")
print("CSV saved")

upload_to_s3("flight_data.csv", "test/flight_data.csv")
