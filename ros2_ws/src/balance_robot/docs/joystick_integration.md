# Joystick / Remote Control Integration Plan

This document describes the planned integration for wireless USB game controller input on the balance robot. It is planning only; no joystick code has been added yet.

## Hardware Scope

The robot will later use a wireless USB game controller connected to the Raspberry Pi 5.

The controller is intended for user movement commands, not for replacing the balance controller.

## Control Architecture

The balance robot will use a layered control model:

- The LQR/balance controller remains responsible for keeping the robot stable.
- A future `joystick_node` will publish user movement intent on a dedicated topic.
- The balance controller will incorporate user commands as a reference or bias while still enforcing stability and safety limits.

The wireless game controller will not replace the balance controller.

## User Movement Commands

The future `joystick_node` will translate controller input into high-level movement commands such as:

- Forward
- Backward
- Turn left
- Turn right
- Stop

These commands represent user intent, not direct motor PWM output.

## Future ROS 2 Topic

A future `joystick_node` will publish user commands on:

```text
/joy_cmd
```

The topic name is planned in `config/robot_params.yaml`:

```yaml
joystick:
  enabled: false
  device: TODO
  topic: /joy_cmd
```

The final message type for `/joy_cmd` has not been defined yet. It should express normalized movement intent that the LQR/balance controller can combine with `RobotState` feedback.

## Relation to Existing Nodes

Current planned data flow:

```text
joystick_node  ->  /joy_cmd
state_estimator_node  ->  /robot_state
lqr_controller_node  ->  /motor_command
motor_node  ->  motor driver
```

The `lqr_controller_node` will remain the authority for motor commands sent to `motor_node`. User input from the joystick will influence the controller reference, not bypass it.

## Raspberry Pi Hardware Testing

When hardware integration begins on the Raspberry Pi, planned checks include:

1. Confirm the USB controller is detected:
   ```bash
   lsusb
   ```

2. If needed, use the ROS 2 `joy` package to verify raw joystick input:
   ```bash
   ros2 run joy joy_node
   ros2 topic echo /joy
   ```

3. Identify the controller device path and map buttons/axes to movement commands.

4. Record the final device identifier in `joystick.device` in `config/robot_params.yaml`.

## Parameters

Planned parameters from `config/robot_params.yaml`:

```yaml
joystick:
  enabled: false
  device: TODO
  topic: /joy_cmd
```

- `enabled`: whether joystick input is active.
- `device`: USB device path or identifier once hardware is selected.
- `topic`: ROS 2 topic for published user movement commands.

## Implementation TODO List

- Select a wireless USB game controller compatible with Raspberry Pi 5.
- Verify controller detection with `lsusb`.
- Evaluate whether to use `ros2 joy` as an intermediate input source.
- Define the message type for `/joy_cmd`.
- Implement `joystick_node` to publish user movement commands.
- Integrate `/joy_cmd` into `lqr_controller_node` without bypassing balance control.
- Test stop behavior and ensure joystick input respects `control.safety_angle_limit_deg`.
- Keep `joystick.enabled: false` until hardware testing is complete.
