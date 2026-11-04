import codrone_edu.drone as codrone
from codrone_edu.drone import *
import math
import time
import csv
import boto3

from real_time_drone_data import RealTimeDroneData

# drone var
drone = codrone.Drone()


# collects data from the drone and packages it into an object
def collect_realtime_drone_data(previous_data):

    # gyroscope
    x_angular_speed = drone.get_angular_speed_x()
    y_angular_speed = drone.get_angular_speed_y()
    z_angular_speed = drone.get_angular_speed_z()
    yaw_angle = drone.get_angle_z()

    # accelerometer (/10 to convert to m/s^2)
    x_accel = drone.get_accel_x() / 10
    y_accel = drone.get_accel_y() / 10
    z_accel = drone.get_accel_z() / 10

    # bottom range sensor
    height = drone.get_height("m")

    # barometer
    pressure = drone.get_pressure()

    # front range sensor
    front_range = drone.get_front_range("m")

    # optical flow sensor
    x_flow = drone.get_flow_velocity_x()
    y_flow = drone.get_flow_velocity_y()

    # color sensors: collect only while landed
    color_data = None
    if drone.get_flight_state() == ModeFlight.Ready:
        color_data = drone.get_color_data().copy()

    # position in meters
    x_position = drone.get_pos_x("m")
    y_position = drone.get_pos_y("m")
    z_position = drone.get_pos_z("m")

    # record the time after reading the positions
    timestamp = time.time()

    # need two readings to estimate speed
    speed_mps = None

    if previous_data is not None:
        elapsed_time = timestamp - previous_data.timestamp

        if elapsed_time > 0:
            x_change = x_position - previous_data.x_position
            y_change = y_position - previous_data.y_position
            z_change = z_position - previous_data.z_position

            distance = math.sqrt(x_change**2 + y_change**2 + z_change**2)

            speed_mps = distance / elapsed_time

    return RealTimeDroneData(
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
    )


def save_to_csv(real_time_drone_data_list, filename):
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(
            [
                "timestamp",
                "x_angular_speed",
                "y_angular_speed",
                "z_angular_speed",
                "x_accel",
                "y_accel",
                "z_accel",
                "height",
                "yaw_angle",
                "pressure",
                "front_range",
                "x_flow",
                "y_flow",
                "color_data",
                "x_position",
                "y_position",
                "z_position",
                "speed_mps",
            ]
        )

        for data in real_time_drone_data_list:
            writer.writerow(
                [
                    data.timestamp,
                    data.x_angular_speed,
                    data.y_angular_speed,
                    data.z_angular_speed,
                    data.x_accel,
                    data.y_accel,
                    data.z_accel,
                    data.height,
                    data.yaw_angle,
                    data.pressure,
                    data.front_range,
                    data.x_flow,
                    data.y_flow,
                    data.color_data,
                    data.x_position,
                    data.y_position,
                    data.z_position,
                    data.speed_mps,
                ]
            )


# # uploads a saved file to our S3 bucket
# uploads a saved file to our S3 bucket
def upload_to_s3(filename, object_name):
    session = boto3.Session(profile_name="drone-lab", region_name="us-east-1")

    s3 = session.client("s3")
    s3.upload_file(filename, "drone-milestone1", object_name)

    print(f"Uploaded to S3: {object_name}")


if __name__ == "__main__":
    # collection to store our real time data
    real_time_drone_data_list = []

    active_flight_session = True
    take_off_recorded = False

    previous_data = None

    try:
        drone.pair()

        print("Collecting data. Keep the drone landed for color readings first.")
        print("Then use the controller to take off, fly, and land.")
        print("Press Ctrl+C to stop collection manually.")

        # this while loop runs once every 0.1 second, and add a new data point
        while active_flight_session:
            flight_state = drone.get_flight_state()

            # if there is a crash/error stop the data collection loop
            if flight_state in (ModeFlight.Accident, ModeFlight.Error, ModeFlight.Stop):
                print("Flight stopped.")
                active_flight_session = False

            else:

                # speed uses prev data and the current one we are collecting
                if flight_state != ModeFlight.Flight:
                    previous_data = None

                real_time_data = collect_realtime_drone_data(previous_data)

                if flight_state == ModeFlight.Flight:
                    previous_data = real_time_data

                # add curr data to list
                real_time_drone_data_list.append(real_time_data)

                print(real_time_data)
                print("\n")

                # if flight is taking off or already happening, record that take off has happened
                if flight_state in (ModeFlight.TakeOff, ModeFlight.Flight):
                    take_off_recorded = True

                # if the flightjn is in ready mode (landed) and we already recorded a takeoff, then the drone has landed
                # we can end the flight session
                elif flight_state == ModeFlight.Ready and take_off_recorded:
                    print("Drone has landed.")
                    active_flight_session = False

            time.sleep(0.1)

    # handle keyboard interrupting the program in console
    except KeyboardInterrupt:
        print("\nCollection stopped. Land with the controller if still flying.")

    # close drone connection
    finally:
        # stop the background reader
        drone._flagThreadRun = False

        # unblock any pending serial read
        if drone._serialport is not None:
            if drone._serialport.is_open:
                drone._serialport.cancel_read()

        # close waits for the reader thread, then closes the port
        drone.close()

        # print total readings collected
        print(f"Total readings collected: {len(real_time_drone_data_list)}")

        if len(real_time_drone_data_list) > 0:
            # save locally first
            filename = f"flight_data_{time.strftime('%Y-%m-%d_%H-%M-%S')}.csv"
            save_to_csv(real_time_drone_data_list, filename)
            print(f"Data saved to {filename}")

            # upload the same file
            object_name = f"flights/{filename}"

            try:
                upload_to_s3(filename, object_name)

            except Exception as error:
                print(f"S3 upload failed: {error}")
                print(f"Your data is still saved locally in {filename}")

        else:
            print("No readings collected. Skipping saving and upload.")
