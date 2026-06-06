import rclpy
from balance_robot.hal import create_encoder
from balance_robot.msg import WheelState
from rclpy.node import Node


class EncoderNode(Node):
    def __init__(self):
        super().__init__('encoder_node')
        self.declare_parameter('control.mode', 'mock')
        self.mode = self.get_parameter('control.mode').value
        self.encoder = create_encoder(self.mode, self.get_logger())
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
