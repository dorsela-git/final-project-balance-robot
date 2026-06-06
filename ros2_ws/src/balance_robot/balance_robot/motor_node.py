import rclpy
from balance_robot.hal import create_motor_driver
from balance_robot.msg import MotorCommand
from rclpy.node import Node


class MotorNode(Node):
    def __init__(self):
        super().__init__('motor_node')
        self.declare_parameter('control.mode', 'mock')
        self.mode = self.get_parameter('control.mode').value
        self.motor_driver = create_motor_driver(self.mode, self.get_logger())
        self.command_subscription = self.create_subscription(
            MotorCommand,
            '/motor_command',
            self.command_callback,
            10,
        )

    def command_callback(self, msg):
        self.motor_driver.apply_command(msg.left_motor, msg.right_motor)


def main(args=None):
    rclpy.init(args=args)
    node = MotorNode()
    try:
        rclpy.spin(node)
    finally:
        node.motor_driver.close()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
