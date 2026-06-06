# Motor Driver Integration Plan

This document describes the planned integration for the balance robot motor driver. It is documentation only; no GPIO or PWM code has been added yet.

## Hardware Scope

The balance robot will use two DC motors:

- Left motor
- Right motor

The motors will be controlled through a motor driver connected to Raspberry Pi 5 GPIO and PWM-capable outputs.

The final motor driver has not been selected yet.

## Raspberry Pi GPIO/PWM Control

The expected control interface is:

- One PWM signal per motor for speed command.
- One direction signal per motor for forward/reverse direction.

Planned parameters from `config/robot_params.yaml`:

```yaml
motors:
  driver: TODO
  left_pwm_pin: TODO
  left_dir_pin: TODO
  right_pwm_pin: TODO
  right_dir_pin: TODO
  pwm_frequency_hz: 1000
  max_command: 1.0
```

The selected pins must be compatible with the Raspberry Pi 5 GPIO library and the chosen motor driver.

## `MotorCommand.msg`

The `motor_node` subscribes to:

```text
/motor_command
```

Message type:

```text
balance_robot/msg/MotorCommand
```

Message fields:

```text
float32 left_motor
float32 right_motor
```

## Command Meaning

The planned command range is normalized:

```text
-max_command <= command <= max_command
```

With the current configuration:

```yaml
max_command: 1.0
```

Command interpretation:

- `0.0`: motor stopped.
- Positive value: forward motor command.
- Negative value: reverse motor command.
- Absolute value: normalized PWM duty command.

Examples:

- `left_motor: 0.5` means left motor forward at 50% of the configured maximum command.
- `right_motor: -0.25` means right motor reverse at 25% of the configured maximum command.

The final sign convention must match the encoder sign convention:

- Positive left and right motor commands should move the robot forward.
- Opposite command signs should rotate the robot in place.

## `motor_node` Integration Plan

The current `motor_node` logs received `MotorCommand` messages. The hardware implementation will keep the ROS interface unchanged and replace logging-only behavior with motor driver output.

Planned responsibilities:

- Load motor parameters from `config/robot_params.yaml`.
- Initialize the selected motor driver.
- Set both motors to stopped during startup.
- Subscribe to `/motor_command`.
- Clamp `left_motor` and `right_motor` to `[-max_command, max_command]`.
- Convert command sign to direction GPIO.
- Convert command magnitude to PWM duty cycle.
- Stop both motors during node shutdown.

## Safety Notes

The first hardware implementation must prioritize safe motor behavior.

Required safety behavior:

- Stop both motors on startup before accepting commands.
- Clamp all commands using `max_command`.
- Stop both motors if command messages time out.
- Stop both motors if the robot tilt exceeds `control.safety_angle_limit_deg`.
- Stop both motors on node shutdown or exception.

Relevant parameter from `config/robot_params.yaml`:

```yaml
control:
  safety_angle_limit_deg: 25.0
```

The large-tilt safety stop will require the motor node or a supervisor to receive robot tilt information from the state estimator before hardware operation.

## Hardware TODO List

- Select the motor driver board.
- Confirm the motor driver supports the motor voltage and current requirements.
- Select Raspberry Pi 5 pins for `left_pwm_pin`, `left_dir_pin`, `right_pwm_pin`, and `right_dir_pin`.
- Confirm whether the motor driver requires enable, standby, brake, or fault pins.
- Confirm Raspberry Pi 3.3V GPIO compatibility with the motor driver logic inputs.
- Test PWM generation at `pwm_frequency_hz: 1000`.
- Test each motor with the wheels off the ground.
- Verify motor direction sign against encoder direction sign.
- Measure minimum PWM needed to overcome static friction.
- Validate `max_command` limiting before closed-loop balancing tests.
- Confirm motors stop when `motor_node` is interrupted.
- Confirm motors stop when `/motor_command` messages stop arriving.
