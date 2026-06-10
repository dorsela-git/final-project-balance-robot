import rclpy
from balance_robot.msg import RobotState, SystemStatus, WheelState
from balance_robot.param_utils import NODE_PARAM_AUTO_DECLARE, get_param_or_default
from balance_robot.safety_state import RobotMode
from rclpy.node import Node
from sensor_msgs.msg import Imu
from std_msgs.msg import String


class TopicHealth:
    def __init__(self):
        self.last_msg_time = None
        self.message_count = 0
        self.frequency_hz = 0.0
        self._window_start = None
        self._window_count = 0

    def record_message(self, now_sec: float) -> None:
        self.last_msg_time = now_sec
        self.message_count += 1

        if self._window_start is None:
            self._window_start = now_sec
            self._window_count = 1
            return

        self._window_count += 1
        window_duration = now_sec - self._window_start
        if window_duration >= 1.0:
            self.frequency_hz = self._window_count / window_duration
            self._window_start = now_sec
            self._window_count = 0

    def is_healthy(self, now_sec: float, stale_timeout_sec: float, min_frequency_hz: float) -> bool:
        if self.last_msg_time is None:
            return False

        age_sec = now_sec - self.last_msg_time
        if age_sec > stale_timeout_sec:
            return False

        if self.frequency_hz > 0.0 and self.frequency_hz < min_frequency_hz:
            return False

        return True


class DiagnosticsNode(Node):
    def __init__(self):
        super().__init__('diagnostics_node', **NODE_PARAM_AUTO_DECLARE)

        self.mode = get_param_or_default(self, 'control.mode', 'mock')
        self.stale_timeout_sec = get_param_or_default(
            self,
            'diagnostics.stale_timeout_sec',
            0.5,
        )
        self.min_frequency_hz = get_param_or_default(
            self,
            'diagnostics.min_frequency_hz',
            10.0,
        )
        publish_rate_hz = get_param_or_default(
            self,
            'diagnostics.publish_rate_hz',
            10.0,
        )
        self.robot_mode = RobotMode.IDLE.value

        self.imu_health = TopicHealth()
        self.encoders_health = TopicHealth()
        self.estimator_health = TopicHealth()

        self.create_subscription(Imu, '/imu/data', self.imu_callback, 10)
        self.create_subscription(WheelState, '/wheel_states', self.encoder_callback, 10)
        self.create_subscription(RobotState, '/robot_state', self.estimator_callback, 10)
        self.create_subscription(String, '/robot_mode', self.robot_mode_callback, 10)
        self.publisher = self.create_publisher(SystemStatus, '/system_status', 10)
        self.timer = self.create_timer(1.0 / publish_rate_hz, self.publish_status)

    def _now_sec(self) -> float:
        return self.get_clock().now().nanoseconds / 1e9

    def imu_callback(self, msg):
        del msg
        self.imu_health.record_message(self._now_sec())

    def encoder_callback(self, msg):
        del msg
        self.encoders_health.record_message(self._now_sec())

    def estimator_callback(self, msg):
        del msg
        self.estimator_health.record_message(self._now_sec())

    def robot_mode_callback(self, msg: String) -> None:
        try:
            self.robot_mode = RobotMode.from_string(msg.data).value
        except ValueError:
            self.get_logger().warn(f'Ignoring invalid robot mode: {msg.data}')

    def _controller_is_healthy(self) -> bool:
        node_names = {name.lstrip('/') for name in self.get_node_names()}
        if 'lqr_controller_node' not in node_names:
            return False

        return self.count_publishers('/motor_command') > 0

    def publish_status(self):
        now_sec = self._now_sec()
        status = SystemStatus()
        status.mode = self.mode
        status.robot_mode = self.robot_mode
        status.imu_ok = self.imu_health.is_healthy(
            now_sec, self.stale_timeout_sec, self.min_frequency_hz
        )
        status.encoders_ok = self.encoders_health.is_healthy(
            now_sec, self.stale_timeout_sec, self.min_frequency_hz
        )
        status.estimator_ok = self.estimator_health.is_healthy(
            now_sec, self.stale_timeout_sec, self.min_frequency_hz
        )
        status.controller_ok = self._controller_is_healthy()
        self.publisher.publish(status)


def main(args=None):
    rclpy.init(args=args)
    node = DiagnosticsNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
