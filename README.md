# final-project-balance-robot

Two-wheeled self-balancing robot using **ROS 2 Jazzy**, **Raspberry Pi 5**, **SparkFun BNO086 IMU**, **wheel encoders**, a **motor driver**, and **LQR control**.

The project provides a mock-first ROS 2 software stack with a hardware abstraction layer, launch files, configuration, diagnostics, and integration planning docs for future Pi hardware bring-up.

## Current Architecture

```text
imu_node ---------------> state_estimator_node -----> lqr_controller_node -----> motor_node
                              ^                              |
encoder_node -----------------+                              v
                                                        /motor_command

diagnostics_node monitors /imu/data, /wheel_states, and /robot_state
diagnostics_node publishes /system_status
```

| Node | Role |
| --- | --- |
| `imu_node` | Publishes IMU data |
| `encoder_node` | Publishes wheel encoder state |
| `state_estimator_node` | Fuses IMU and encoder data into robot state |
| `lqr_controller_node` | Computes motor commands and applies safety stop logic |
| `motor_node` | Receives motor commands and drives the motor HAL |
| `diagnostics_node` | Monitors topic health and publishes system status |

## Topics

| Topic | Message Type | Publisher | Subscriber(s) |
| --- | --- | --- | --- |
| `/imu/data` | `sensor_msgs/msg/Imu` | `imu_node` | `state_estimator_node`, `diagnostics_node` |
| `/wheel_states` | `balance_robot/msg/WheelState` | `encoder_node` | `state_estimator_node`, `diagnostics_node` |
| `/robot_state` | `balance_robot/msg/RobotState` | `state_estimator_node` | `lqr_controller_node`, `diagnostics_node` |
| `/motor_command` | `balance_robot/msg/MotorCommand` | `lqr_controller_node` | `motor_node` |
| `/system_status` | `balance_robot/msg/SystemStatus` | `diagnostics_node` | — |

## Repository Structure

```text
final-project-balance-robot/
├── docker/                         # Docker image and container setup
├── .devcontainer/                    # VS Code / Cursor dev container config
├── docs/                             # Repository-level documentation
├── ros2_ws/
│   └── src/balance_robot/
│       ├── balance_robot/            # Python nodes and HAL
│       │   └── hal/                  # Hardware abstraction layer
│       ├── config/                   # robot_params.yaml
│       ├── launch/                   # robot.launch.py
│       ├── msg/                      # Custom ROS 2 messages
│       ├── docs/                     # Hardware integration plans
│       └── scripts/                  # Node executables
├── docker-compose.yml
└── README.md
```

## Development Commands

```bash
cd /ros2_ws
colcon build --packages-select balance_robot
source install/setup.bash
ros2 launch balance_robot robot.launch.py
ros2 topic echo /system_status balance_robot/msg/SystemStatus
```

## Control Modes

The stack is configured through `config/robot_params.yaml`:

### `control.mode = mock`

- Default development mode.
- Nodes use mock HAL implementations.
- Dummy sensor data and logged motor commands are published.
- Full ROS 2 communication chain can be tested without hardware.

### `control.mode = hardware`

- Selects hardware HAL placeholder classes.
- Logs TODO messages for future BNO086, encoder, and motor driver integration.
- No real GPIO, I2C, or motor driver code is implemented yet.

## Current Status

- Mock ROS 2 stack works end-to-end.
- Custom messages, launch file, diagnostics, and HAL foundation are in place.
- Hardware-specific driver code is **not implemented yet**.
- Integration planning docs exist for IMU, encoders, motors, and joystick input.

## Hardware Integration Docs

See `ros2_ws/src/balance_robot/docs/`:

- `bno086_integration.md`
- `encoder_integration.md`
- `motor_driver_integration.md`
- `joystick_integration.md`
