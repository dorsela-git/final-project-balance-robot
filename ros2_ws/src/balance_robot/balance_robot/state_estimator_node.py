import math

import rclpy
from balance_robot.msg import RobotState, WheelState
from balance_robot.param_utils import NODE_PARAM_AUTO_DECLARE, get_param_or_default
from rclpy.node import Node
from sensor_msgs.msg import Imu

IMU_STALE_TIMEOUT_SEC = 0.1

_GYRO_AXIS_GETTERS = {
    'x': lambda velocity: velocity.x,
    'y': lambda velocity: velocity.y,
    'z': lambda velocity: velocity.z,
}


def _quaternion_to_pitch(x: float, y: float, z: float, w: float) -> float:
    sin_pitch = 2.0 * ((w * y) - (z * x))
    sin_pitch = max(-1.0, min(1.0, sin_pitch))
    return math.asin(sin_pitch)


class StateEstimatorNode(Node):
    def __init__(self):
        super().__init__('state_estimator_node', **NODE_PARAM_AUTO_DECLARE)

        self.imu_topic = get_param_or_default(self, 'estimator.imu_topic', '/imu/data')
        self.theta_sign = get_param_or_default(self, 'estimator.theta_sign', 1.0)
        self.theta_dot_sign = get_param_or_default(self, 'estimator.theta_dot_sign', 1.0)
        self.theta_offset_rad = get_param_or_default(
            self,
            'estimator.theta_offset_rad',
            0.0,
        )
        self.encoder_stale_timeout_sec = get_param_or_default(
            self,
            'estimator.encoder_stale_timeout_sec',
            0.1,
        )
        self.left_wheel_sign = get_param_or_default(
            self,
            'estimator.left_wheel_sign',
            1.0,
        )
        self.right_wheel_sign = get_param_or_default(
            self,
            'estimator.right_wheel_sign',
            1.0,
        )
        self.x_sign = get_param_or_default(self, 'estimator.x_sign', 1.0)
        self.x_offset_m = get_param_or_default(self, 'estimator.x_offset_m', 0.0)
        theta_dot_axis = get_param_or_default(self, 'estimator.theta_dot_axis', 'y')
        if theta_dot_axis not in _GYRO_AXIS_GETTERS:
            raise ValueError(
                f'estimator.theta_dot_axis must be x, y, or z; got {theta_dot_axis!r}'
            )
        self.theta_dot_axis = theta_dot_axis

        self.imu_subscription = self.create_subscription(
            Imu,
            self.imu_topic,
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
        self.latest_imu_time_sec = None
        self.latest_encoders = None
        self.latest_encoder_time_sec = None

    def imu_callback(self, msg):
        self.latest_imu = msg
        self.latest_imu_time_sec = self.get_clock().now().nanoseconds / 1e9

    def encoder_callback(self, msg):
        self.latest_encoders = msg
        self.latest_encoder_time_sec = self.get_clock().now().nanoseconds / 1e9

    def _imu_is_stale(self) -> bool:
        if self.latest_imu is None or self.latest_imu_time_sec is None:
            return True
        now_sec = self.get_clock().now().nanoseconds / 1e9
        return (now_sec - self.latest_imu_time_sec) > IMU_STALE_TIMEOUT_SEC

    def _encoders_are_stale(self) -> bool:
        if self.latest_encoders is None or self.latest_encoder_time_sec is None:
            return True
        now_sec = self.get_clock().now().nanoseconds / 1e9
        return (
            now_sec - self.latest_encoder_time_sec
        ) > self.encoder_stale_timeout_sec

    def _wheel_state_to_x(self, wheel_msg: WheelState):
        left_position = self.left_wheel_sign * wheel_msg.left_position
        right_position = self.right_wheel_sign * wheel_msg.right_position
        left_velocity = self.left_wheel_sign * wheel_msg.left_velocity
        right_velocity = self.right_wheel_sign * wheel_msg.right_velocity

        x = (
            self.x_sign * ((left_position + right_position) / 2.0)
            - self.x_offset_m
        )
        x_dot = self.x_sign * ((left_velocity + right_velocity) / 2.0)
        return x, x_dot

    def _imu_to_theta(self, imu_msg: Imu):
        orientation = imu_msg.orientation
        norm = math.sqrt(
            orientation.x ** 2
            + orientation.y ** 2
            + orientation.z ** 2
            + orientation.w ** 2
        )
        if norm < 1e-6:
            return None

        if abs(norm - 1.0) > 1e-3:
            quaternion = [
                orientation.x / norm,
                orientation.y / norm,
                orientation.z / norm,
                orientation.w / norm,
            ]
        else:
            quaternion = [
                orientation.x,
                orientation.y,
                orientation.z,
                orientation.w,
            ]

        pitch = _quaternion_to_pitch(*quaternion)
        theta = (self.theta_sign * pitch) - self.theta_offset_rad
        angular_velocity = imu_msg.angular_velocity
        theta_dot = (
            self.theta_dot_sign
            * _GYRO_AXIS_GETTERS[self.theta_dot_axis](angular_velocity)
        )
        return theta, theta_dot

    def publish_state(self):
        if self._imu_is_stale() or self._encoders_are_stale():
            return

        estimate = self._imu_to_theta(self.latest_imu)
        if estimate is None:
            return

        theta, theta_dot = estimate
        x, x_dot = self._wheel_state_to_x(self.latest_encoders)
        msg = RobotState()
        msg.x = x
        msg.x_dot = x_dot
        msg.theta = theta
        msg.theta_dot = theta_dot
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
