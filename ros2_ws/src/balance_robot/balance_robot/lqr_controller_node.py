import math

import rclpy
from balance_robot.msg import MotorCommand, RobotState
from rclpy.node import Node


class LqrControllerNode(Node):
    def __init__(self):
        super().__init__('lqr_controller_node')
        self.declare_parameter('control.mode', 'mock')
        self.declare_parameter('control.safety_angle_limit_deg', 25.0)
        self.mode = self.get_parameter('control.mode').value
        safety_angle_limit_deg = self.get_parameter(
            'control.safety_angle_limit_deg'
        ).value
        self.safety_angle_limit_rad = math.radians(safety_angle_limit_deg)
        self.safety_stop_active = False
        if self.mode == 'hardware':
            self.get_logger().warn(
                'TODO: hardware mode selected for lqr_controller_node, '
                'but real LQR control is not implemented yet.'
            )
        self.state_subscription = self.create_subscription(
            RobotState,
            '/robot_state',
            self.state_callback,
            10,
        )
        self.publisher = self.create_publisher(MotorCommand, '/motor_command', 10)
        self.timer = self.create_timer(0.02, self.publish_motor_command)
        self.latest_state = None

    def state_callback(self, msg):
        self.latest_state = msg
        self.safety_stop_active = abs(msg.theta) > self.safety_angle_limit_rad
        if self.safety_stop_active:
            stop_command = MotorCommand()
            stop_command.left_motor = 0.0
            stop_command.right_motor = 0.0
            self.publisher.publish(stop_command)
            self.get_logger().warn(
                'Safety stop triggered: theta exceeds '
                f'{self.safety_angle_limit_rad:.3f} rad limit.'
            )

    def publish_motor_command(self):
        if self.mode == 'hardware':
            return

        if self.safety_stop_active:
            msg = MotorCommand()
            msg.left_motor = 0.0
            msg.right_motor = 0.0
            self.publisher.publish(msg)
            return

        # TODO: Implement real LQR gains.
        msg = MotorCommand()
        msg.left_motor = 0.0
        msg.right_motor = 0.0
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
