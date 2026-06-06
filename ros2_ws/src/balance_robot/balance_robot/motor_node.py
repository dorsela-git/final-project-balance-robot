import rclpy
from balance_robot.hal import create_motor_driver
from balance_robot.msg import MotorCommand
from balance_robot.safety_state import RobotMode
from rclpy.node import Node
from std_msgs.msg import String


class MotorNode(Node):
    def __init__(self):
        super().__init__('motor_node')
        self.declare_parameter('control.mode', 'mock')
        self.declare_parameter('safety.allow_motor_commands_only_in_balancing', True)

        self.mode = self.get_parameter('control.mode').value
        self.allow_motor_commands_only_in_balancing = (
            self.get_parameter('safety.allow_motor_commands_only_in_balancing').value
        )
        self.robot_mode = RobotMode.IDLE

        self.motor_driver = create_motor_driver(self.mode, self.get_logger())
        self.motor_driver.stop()
        self.create_subscription(String, '/robot_mode', self._robot_mode_callback, 10)
        self.command_subscription = self.create_subscription(
            MotorCommand,
            '/motor_command',
            self.command_callback,
            10,
        )

    def _robot_mode_callback(self, msg: String) -> None:
        try:
            previous_mode = self.robot_mode
            self.robot_mode = RobotMode.from_string(msg.data)
        except ValueError:
            self.get_logger().warn(f'Ignoring invalid robot mode: {msg.data}')
            return

        if (
            previous_mode == RobotMode.BALANCING
            and self.robot_mode != RobotMode.BALANCING
            and self.allow_motor_commands_only_in_balancing
        ):
            self.motor_driver.stop()

    def _motor_commands_allowed(self) -> bool:
        if not self.allow_motor_commands_only_in_balancing:
            return True
        return self.robot_mode == RobotMode.BALANCING

    def command_callback(self, msg):
        if not self._motor_commands_allowed():
            return

        self.motor_driver.apply_command(msg.left_motor, msg.right_motor)


def main(args=None):
    rclpy.init(args=args)
    node = MotorNode()
    try:
        rclpy.spin(node)
    finally:
        node.motor_driver.stop()
        node.motor_driver.close()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
