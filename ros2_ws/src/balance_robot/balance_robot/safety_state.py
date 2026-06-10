from enum import Enum

import rclpy
from balance_robot.param_utils import NODE_PARAM_AUTO_DECLARE, get_param_or_default
from rclpy.node import Node
from std_msgs.msg import String


class RobotMode(Enum):
    IDLE = 'IDLE'
    ARMED = 'ARMED'
    BALANCING = 'BALANCING'
    FAULT = 'FAULT'
    ESTOP = 'ESTOP'

    @classmethod
    def from_string(cls, value: str) -> 'RobotMode':
        normalized = value.strip().upper()
        try:
            return cls(normalized)
        except ValueError as exc:
            raise ValueError(f'Unknown robot mode: {value}') from exc


class InvalidTransitionError(Exception):
    pass


class SafetyStateManager:
    _NORMAL_TRANSITIONS = {
        RobotMode.IDLE: {RobotMode.ARMED},
        RobotMode.ARMED: {RobotMode.BALANCING},
    }

    def __init__(self, startup_mode: RobotMode = RobotMode.IDLE):
        self._mode = startup_mode

    @property
    def mode(self) -> RobotMode:
        return self._mode

    def request_transition(self, target: RobotMode) -> None:
        if target == self._mode:
            return

        if target in (RobotMode.FAULT, RobotMode.ESTOP):
            self._mode = target
            return

        allowed = self._NORMAL_TRANSITIONS.get(self._mode, set())
        if target not in allowed:
            raise InvalidTransitionError(
                f'Transition {self._mode.value} -> {target.value} is not allowed'
            )

        self._mode = target

    def reset(self) -> None:
        if self._mode not in (RobotMode.FAULT, RobotMode.ESTOP):
            raise InvalidTransitionError(
                f'Reset is only allowed from FAULT or ESTOP, current mode is {self._mode.value}'
            )
        self._mode = RobotMode.IDLE

    def motor_commands_allowed(self, only_in_balancing: bool) -> bool:
        if not only_in_balancing:
            return True
        return self._mode == RobotMode.BALANCING


class SafetyStateNode(Node):
    def __init__(self):
        super().__init__('safety_state_node', **NODE_PARAM_AUTO_DECLARE)

        startup_mode = RobotMode.from_string(
            get_param_or_default(self, 'safety.startup_mode', 'IDLE')
        )
        publish_rate_hz = get_param_or_default(self, 'safety.publish_rate_hz', 10.0)

        self._manager = SafetyStateManager(startup_mode=startup_mode)
        self._mode_publisher = self.create_publisher(String, '/robot_mode', 10)
        self.create_subscription(
            String,
            '/robot_mode/request',
            self._request_callback,
            10,
        )
        self._timer = self.create_timer(1.0 / publish_rate_hz, self._publish_mode)
        self._publish_mode()
        self.get_logger().info(f'Robot mode initialized to {self._manager.mode.value}')

    def _publish_mode(self) -> None:
        msg = String()
        msg.data = self._manager.mode.value
        self._mode_publisher.publish(msg)

    def _request_callback(self, msg: String) -> None:
        command = msg.data.strip().upper()
        if not command:
            return

        try:
            if command == 'RESET':
                self._manager.reset()
            else:
                self._manager.request_transition(RobotMode.from_string(command))
        except (InvalidTransitionError, ValueError) as exc:
            self.get_logger().warn(str(exc))
            return

        self.get_logger().info(f'Robot mode is now {self._manager.mode.value}')
        self._publish_mode()


def main(args=None):
    rclpy.init(args=args)
    node = SafetyStateNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
