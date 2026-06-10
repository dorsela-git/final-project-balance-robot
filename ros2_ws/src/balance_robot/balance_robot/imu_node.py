import rclpy
from balance_robot.hal import create_imu
from balance_robot.param_utils import NODE_PARAM_AUTO_DECLARE, get_param_or_default
from rclpy.node import Node
from sensor_msgs.msg import Imu


class ImuNode(Node):
    def __init__(self):
        super().__init__('imu_node', **NODE_PARAM_AUTO_DECLARE)
        self.mode = get_param_or_default(self, 'control.mode', 'mock')
        self.imu = create_imu(self.mode, self.get_logger(), self)
        self.publisher = self.create_publisher(Imu, '/imu/data', 10)
        self.timer = self.create_timer(0.02, self.publish_imu)

    def publish_imu(self):
        msg = self.imu.read(
            self.get_clock().now().to_msg(),
            'imu_link',
        )
        if msg is not None:
            self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = ImuNode()
    try:
        rclpy.spin(node)
    finally:
        node.imu.close()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
