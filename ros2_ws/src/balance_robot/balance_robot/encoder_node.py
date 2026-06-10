import rclpy
from balance_robot.hal import create_encoder
from balance_robot.msg import WheelState
from balance_robot.param_utils import NODE_PARAM_AUTO_DECLARE, get_param_or_default
from rclpy.node import Node


class EncoderNode(Node):
    def __init__(self):
        super().__init__('encoder_node', **NODE_PARAM_AUTO_DECLARE)
        self.mode = get_param_or_default(self, 'control.mode', 'mock')
        self.encoder = create_encoder(self.mode, self.get_logger(), self)
        self.publisher = self.create_publisher(WheelState, '/wheel_states', 10)
        self.timer = self.create_timer(0.02, self.publish_encoders)

    def publish_encoders(self):
        msg = self.encoder.read()
        if msg is not None:
            self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = EncoderNode()
    try:
        rclpy.spin(node)
    finally:
        node.encoder.close()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
