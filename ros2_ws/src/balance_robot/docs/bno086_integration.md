# SparkFun BNO086 IMU Integration Plan

This document describes the planned hardware integration for the SparkFun BNO086 IMU on the balance robot. It is a planning document only; no hardware-specific code has been added yet.

## Raspberry Pi 5 I2C Setup

The BNO086 will communicate with the Raspberry Pi 5 over I2C.

Planned setup steps:

1. Enable I2C on the Raspberry Pi:
   ```bash
   sudo raspi-config
   ```
   Navigate to `Interface Options` -> `I2C` -> enable.

2. Install basic I2C tools:
   ```bash
   sudo apt update
   sudo apt install -y i2c-tools python3-smbus
   ```

3. Confirm the I2C bus is available:
   ```bash
   ls /dev/i2c-*
   ```

4. Scan the default I2C bus:
   ```bash
   sudo i2cdetect -y 1
   ```

On most Raspberry Pi setups, the primary I2C bus is `/dev/i2c-1`.

## BNO086 Wiring

Planned I2C wiring between the Raspberry Pi 5 GPIO header and the SparkFun BNO086 breakout:

| Raspberry Pi 5 | BNO086 Breakout | Purpose |
| --- | --- | --- |
| 3.3V | VIN or 3V3 | Power |
| GND | GND | Ground |
| GPIO 2 / SDA1 | SDA | I2C data |
| GPIO 3 / SCL1 | SCL | I2C clock |

Use 3.3V logic. Do not connect the BNO086 I2C pins to 5V logic.

## I2C Address

The BNO086 default I2C address is expected to be:

```text
0x4A
```

Some breakout configurations may support an alternate address:

```text
0x4B
```

The final address should be confirmed with:

```bash
sudo i2cdetect -y 1
```

## Required Python Libraries

The preferred Python stack is:

- `rclpy` for the ROS 2 node.
- `sensor_msgs` for publishing `sensor_msgs/msg/Imu`.
- SparkFun or Adafruit BNO08x/BNO085/BNO086 Python support library, depending on hardware support and compatibility on Raspberry Pi 5.

Candidate libraries to evaluate:

- `sparkfun-qwiic-bno08x`
- `adafruit-circuitpython-bno08x`
- `smbus2`

The implementation should choose one sensor driver library after validating that it supports the BNO086 over Linux I2C on Raspberry Pi 5.

## ROS 2 Node Design

The existing `imu_node` will remain the owner of IMU publishing.

Planned responsibilities:

- Initialize the BNO086 over I2C during node startup.
- Enable the required BNO086 sensor reports, such as rotation vector, gyroscope, and linear acceleration.
- Read sensor samples on a timer.
- Convert sensor output into `sensor_msgs/msg/Imu`.
- Publish the message on `/imu/data`.
- Log initialization or read failures clearly.

The first hardware implementation should keep the current node interface unchanged so downstream nodes do not need to change.

## Published Topics

The IMU node will publish:

| Topic | Message Type | Description |
| --- | --- | --- |
| `/imu/data` | `sensor_msgs/msg/Imu` | Orientation, angular velocity, and linear acceleration from the BNO086 |

No new IMU topic is planned for the initial integration.

## Message Types

The IMU integration will continue using the standard ROS 2 message:

```text
sensor_msgs/msg/Imu
```

Field mapping plan:

- `header.stamp`: current ROS time from the node clock.
- `header.frame_id`: `imu_link`.
- `orientation`: quaternion from the BNO086 rotation vector.
- `angular_velocity`: gyroscope reading.
- `linear_acceleration`: linear acceleration reading.
- covariance fields: initially set to unknown or conservative placeholder values until measured.

## Expected Update Rate

The target update rate is:

```text
50 Hz
```

This matches the current mock `imu_node` timer period of `0.02` seconds. If the BNO086 driver cannot reliably sustain 50 Hz with the selected reports, the integration should document the measured rate and adjust the timer or report interval deliberately.

## Upgrade Path From Dummy Data

The current `imu_node` publishes mock `sensor_msgs/msg/Imu` data at 50 Hz.

Planned upgrade steps:

1. Add a small BNO086 hardware abstraction inside `imu_node` or a separate helper module.
2. Initialize I2C and the BNO086 during `ImuNode.__init__`.
3. Replace the current dummy message fields in `publish_imu()` with real sensor readings.
4. Preserve the existing topic name `/imu/data`.
5. Preserve the existing message type `sensor_msgs/msg/Imu`.
6. Keep the publish rate at 50 Hz unless hardware testing shows a different rate is required.
7. Add startup logging for detected I2C bus, detected address, and enabled BNO086 reports.
8. Add error handling for temporary read failures without crashing the whole ROS graph.

Downstream nodes should continue subscribing to `/imu/data` and should not need interface changes when the IMU moves from dummy data to real BNO086 data.
