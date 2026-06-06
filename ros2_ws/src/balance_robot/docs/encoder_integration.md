# Wheel Encoder Integration Plan

This document describes the planned integration for the left and right wheel encoders. It is documentation only; no GPIO code has been added yet.

## Hardware Scope

The balance robot will use two wheel encoders:

- Left wheel encoder
- Right wheel encoder

Each encoder is expected to provide quadrature signals:

- Channel A
- Channel B

The two channels allow the software to count ticks and infer direction from the phase relationship between A and B.

## Raspberry Pi 5 GPIO Inputs

The encoder channels will connect to Raspberry Pi 5 GPIO inputs.

Planned parameters from `config/robot_params.yaml`:

```yaml
encoders:
  left_gpio_a: TODO
  left_gpio_b: TODO
  right_gpio_a: TODO
  right_gpio_b: TODO
  ticks_per_revolution: TODO
  wheel_radius_m: TODO
  wheel_base_m: TODO
  publish_rate_hz: 50
```

The final GPIO pin numbers must be selected after checking the motor driver wiring, available pins, and any Raspberry Pi 5 GPIO library limitations.

## Encoder Signals

Each encoder provides:

- `A`: digital pulse train.
- `B`: digital pulse train shifted relative to `A`.

The software will use transitions on the channels to update a signed tick count:

- Forward wheel rotation increments the count.
- Reverse wheel rotation decrements the count.

The exact sign convention should match the robot coordinate frame:

- Positive left and right wheel motion should move the robot forward.
- Opposite wheel signs should correspond to rotation in place.

## `encoder_node` Calculation Plan

The current `encoder_node` publishes mock `WheelState` values. The hardware implementation will replace the mock values with measurements computed from encoder ticks.

### Position

The node will maintain cumulative signed tick counts:

```text
left_ticks
right_ticks
```

Wheel angle in radians:

```text
wheel_angle_rad = ticks * 2*pi / ticks_per_revolution
```

Wheel travel distance in meters:

```text
wheel_position_m = wheel_angle_rad * wheel_radius_m
```

Published fields:

- `left_position`: left wheel travel distance in meters.
- `right_position`: right wheel travel distance in meters.

### Velocity

At each publish interval, the node will compare the current tick count with the previous tick count:

```text
delta_ticks = current_ticks - previous_ticks
delta_time_s = current_time - previous_time
```

Wheel velocity:

```text
wheel_velocity_mps =
  (delta_ticks * 2*pi / ticks_per_revolution) * wheel_radius_m / delta_time_s
```

Published fields:

- `left_velocity`: left wheel linear velocity in meters per second.
- `right_velocity`: right wheel linear velocity in meters per second.

## Relation to `WheelState.msg`

The encoder node publishes:

```text
/wheel_states
```

Message type:

```text
balance_robot/msg/WheelState
```

Message fields:

```text
float32 left_position
float32 right_position
float32 left_velocity
float32 right_velocity
```

The state estimator will consume this topic to estimate robot position and velocity.

## Hardware TODO List

- Select Raspberry Pi 5 GPIO pins for `left_gpio_a`, `left_gpio_b`, `right_gpio_a`, and `right_gpio_b`.
- Confirm encoder voltage levels are safe for Raspberry Pi 3.3V GPIO.
- Confirm whether pull-up or pull-down resistors are required.
- Verify encoder tick polarity for forward and reverse wheel motion.
- Measure or confirm `ticks_per_revolution`.
- Measure `wheel_radius_m`.
- Measure `wheel_base_m`.
- Validate interrupt or polling support with the selected Raspberry Pi 5 GPIO library.
- Test one wheel at low speed and compare measured ticks to expected revolutions.
- Test both wheels simultaneously and verify no missed ticks at expected motor speed.
- Confirm `encoder_node` can publish reliably at `publish_rate_hz: 50`.
