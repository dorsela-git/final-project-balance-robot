import math

import rclpy
from balance_robot.msg import MotorCommand, RobotState
from balance_robot.param_utils import NODE_PARAM_AUTO_DECLARE, get_param_or_default
from rclpy.node import Node

STATE_STALE_TIMEOUT_SEC = 0.1


class LqrControllerNode(Node):
    def __init__(self):
        super().__init__('lqr_controller_node', **NODE_PARAM_AUTO_DECLARE)

        safety_angle_limit_deg = get_param_or_default(
            self,
            'control.safety_angle_limit_deg',
            25.0,
        )
        self.safety_angle_limit_rad = math.radians(safety_angle_limit_deg)
        self.lqr_gain = list(
            get_param_or_default(
                self,
                'control.lqr_gain',
                [0.0, 0.0, 0.0, 0.0],
            )
        )
        self.max_command = get_param_or_default(self, 'motors.max_command', 1.0)

        self.safety_stop_active = False
        self.state_subscription = self.create_subscription(
            RobotState,
            '/robot_state',
            self.state_callback,
            10,
        )
        self.publisher = self.create_publisher(MotorCommand, '/motor_command', 10)
        self.timer = self.create_timer(0.02, self.publish_motor_command)
        self.latest_state = None
        self.latest_state_time_sec = None

    def _now_sec(self) -> float:
        return self.get_clock().now().nanoseconds / 1e9

    def _state_is_stale(self) -> bool:
        if self.latest_state is None or self.latest_state_time_sec is None:
            return True
        return (self._now_sec() - self.latest_state_time_sec) > STATE_STALE_TIMEOUT_SEC

    def _publish_stop(self) -> None:
        msg = MotorCommand()
        msg.left_motor = 0.0
        msg.right_motor = 0.0
        self.publisher.publish(msg)

    def _clamp_command(self, command: float) -> float:
        return max(-self.max_command, min(self.max_command, command))

    def _compute_lqr_command(self, state: RobotState) -> float:
        x = [state.x, state.x_dot, state.theta, state.theta_dot]
        u = -sum(k * xi for k, xi in zip(self.lqr_gain, x))
        return self._clamp_command(u)

    def state_callback(self, msg):
        self.latest_state = msg
        self.latest_state_time_sec = self._now_sec()
        self.safety_stop_active = abs(msg.theta) > self.safety_angle_limit_rad
        if self.safety_stop_active:
            self._publish_stop()
            self.get_logger().warn(
                'Safety stop triggered: theta exceeds '
                f'{self.safety_angle_limit_rad:.3f} rad limit.'
            )

    def publish_motor_command(self):
        if self.safety_stop_active:
            self._publish_stop()
            return

        if self._state_is_stale():
            self._publish_stop()
            return

        u = self._compute_lqr_command(self.latest_state)
        msg = MotorCommand()
        msg.left_motor = u
        msg.right_motor = u
        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = LqrControllerNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
