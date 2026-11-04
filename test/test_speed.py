from unittest.mock import MagicMock, patch
from main import collect_realtime_drone_data, ModeFlight

# pretend drone with known readings
fake_drone = MagicMock()

fake_drone.get_angular_speed_x.return_value = 0
fake_drone.get_angular_speed_y.return_value = 0
fake_drone.get_angular_speed_z.return_value = 0
fake_drone.get_angle_z.return_value = 0

fake_drone.get_accel_x.return_value = 0
fake_drone.get_accel_y.return_value = 0
fake_drone.get_accel_z.return_value = 98

fake_drone.get_height.return_value = 0
fake_drone.get_pressure.return_value = 101325
fake_drone.get_front_range.return_value = 1

fake_drone.get_flow_velocity_x.return_value = 0
fake_drone.get_flow_velocity_y.return_value = 0
fake_drone.get_flight_state.return_value = ModeFlight.Flight

# positions for five consecutive readings
fake_drone.get_pos_x.side_effect = [0, 3, 3, 3, 3]
fake_drone.get_pos_y.side_effect = [0, 4, 4, 4, 4]
fake_drone.get_pos_z.side_effect = [0, 0, 6, 6, 6]

# temporarily replace the drone and clock
with patch("main.drone", fake_drone):
    with patch("main.time.time", side_effect=[10, 12, 14, 16, 16]):
        first = collect_realtime_drone_data(None)
        assert first.speed_mps is None

        # moved 5 meters in 2 seconds
        second = collect_realtime_drone_data(first)
        assert second.speed_mps == 2.5

        # moved vertically 6 meters in 2 seconds
        third = collect_realtime_drone_data(second)
        assert third.speed_mps == 3

        # stayed in the same position for 2 seconds
        fourth = collect_realtime_drone_data(third)
        assert fourth.speed_mps == 0

        # no elapsed time: cannot calculate speed
        fifth = collect_realtime_drone_data(fourth)
        assert fifth.speed_mps is None

print("All speed calculation tests passed")