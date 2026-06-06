import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from std_msgs.msg import String


class TeleopNode(Node):
    def __init__(self):
        super().__init__('teleop_node')
        self.declare_parameter('teleop.enabled', True)
        self.declare_parameter('teleop.arm_button', 0)
        self.declare_parameter('teleop.balance_button', 1)
        self.declare_parameter('teleop.estop_button', 3)
        self.declare_parameter('teleop.reset_button', 6)
        self.declare_parameter('teleop.deadman_button', 4)
        self.declare_parameter('teleop.require_deadman', True)

        self.enabled = self.get_parameter('teleop.enabled').value
        if not self.enabled:
            self.get_logger().info('Teleop disabled by parameter; node will idle.')
            return

        self.arm_button = self.get_parameter('teleop.arm_button').value
        self.balance_button = self.get_parameter('teleop.balance_button').value
        self.estop_button = self.get_parameter('teleop.estop_button').value
        self.reset_button = self.get_parameter('teleop.reset_button').value
        self.deadman_button = self.get_parameter('teleop.deadman_button').value
        self.require_deadman = self.get_parameter('teleop.require_deadman').value

        self._previous_buttons = []
        self._mode_request_publisher = self.create_publisher(String, '/robot_mode/request', 10)
        self.create_subscription(Joy, '/joy', self._joy_callback, 10)
        self.get_logger().info('Teleop node waiting for /joy input.')

    def _button_pressed(self, buttons: list[int], index: int) -> bool:
        if index < 0 or index >= len(buttons):
            return False
        return buttons[index] == 1

    def _rising_edge(self, buttons: list[int], index: int) -> bool:
        if index < 0 or index >= len(buttons):
            return False
        previous = self._previous_buttons[index] if index < len(self._previous_buttons) else 0
        return buttons[index] == 1 and previous == 0

    def _publish_mode_request(self, mode: str) -> None:
        msg = String()
        msg.data = mode
        self._mode_request_publisher.publish(msg)
        self.get_logger().info(f'Published robot mode request: {mode}')

    def _joy_callback(self, msg: Joy) -> None:
        buttons = list(msg.buttons)

        if self._rising_edge(buttons, self.estop_button):
            self._publish_mode_request('ESTOP')

        deadman_active = (
            not self.require_deadman
            or self._button_pressed(buttons, self.deadman_button)
        )
        if deadman_active:
            if self._rising_edge(buttons, self.arm_button):
                self._publish_mode_request('ARMED')
            if self._rising_edge(buttons, self.balance_button):
                self._publish_mode_request('BALANCING')
            if self._rising_edge(buttons, self.reset_button):
                self._publish_mode_request('RESET')

        self._previous_buttons = buttons


def main(args=None):
    rclpy.init(args=args)
    node = TeleopNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
