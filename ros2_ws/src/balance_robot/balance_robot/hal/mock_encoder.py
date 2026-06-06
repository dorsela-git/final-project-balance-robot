from typing import Optional

from balance_robot.msg import WheelState

from balance_robot.hal.base_encoder import BaseEncoder


class MockEncoder(BaseEncoder):
    def read(self) -> Optional[WheelState]:
        msg = WheelState()
        msg.left_position = 0.0
        msg.right_position = 0.0
        msg.left_velocity = 0.0
        msg.right_velocity = 0.0
        return msg
