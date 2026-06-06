from typing import Optional

from sensor_msgs.msg import Imu

from balance_robot.hal.base_imu import BaseIMU


class MockIMU(BaseIMU):
    def read(self, stamp, frame_id: str) -> Optional[Imu]:
        msg = Imu()
        msg.header.stamp = stamp
        msg.header.frame_id = frame_id
        msg.orientation.w = 1.0
        return msg
