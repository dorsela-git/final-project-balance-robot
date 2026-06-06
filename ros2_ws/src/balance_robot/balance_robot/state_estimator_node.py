import rclpy
from balance_robot.msg import RobotState, WheelState
from rclpy.node import Node
from sensor_msgs.msg import Imu


class StateEstimatorNode(Node):
    def __init__(self):
        super().__init__('state_estimator_node')
        self.declare_parameter('control.mode', 'mock')
        self.mode = self.get_parameter('control.mode').value
        if self.mode == 'hardware':
            self.get_logger().warn(
                'TODO: hardware mode selected for state_estimator_node, '
                'but real state estimation is not implemented yet.'
            )
        self.imu_subscription = self.create_subscription(
            Imu,
            '/imu/data',
            self.imu_callback,
            10,
        )
        self.encoder_subscription = self.create_subscription(
            WheelState,
            '/wheel_states',
            self.encoder_callback,
            10,
        )
        self.publisher = self.create_publisher(RobotState, '/robot_state', 10)
        self.timer = self.create_timer(0.02, self.publish_state)
        self.latest_imu = None
        self.latest_encoders = None

    def imu_callback(self, msg):
        self.latest_imu = msg

    def encoder_callback(self, msg):
        self.latest_encoders = msg

    def publish_state(self):
        if self.mode == 'hardware':
            return

        msg = RobotState()
        msg.x = 0.0
        msg.x_dot = 0.0
        msg.theta = 0.0
        msg.theta_dot = 0.0
        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = StateEstimatorNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
