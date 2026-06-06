import math
from typing import Any, Optional

from balance_robot.msg import WheelState

from balance_robot.hal.base_encoder import BaseEncoder


class HardwareEncoder(BaseEncoder):
    """JGB37-520 Hall quadrature encoder foundation for Raspberry Pi GPIO."""

    def __init__(self, logger, node=None):
        self._logger = logger
        self._node = node
        self._left_ticks = 0
        self._right_ticks = 0
        self._previous_timestamp_sec: Optional[float] = None
        self._previous_left_ticks = 0
        self._previous_right_ticks = 0
        self._gpio_ready = False
        self._readiness_logged = False

        self._left_gpio_a = None
        self._left_gpio_b = None
        self._right_gpio_a = None
        self._right_gpio_b = None
        self._ticks_per_revolution = 0.0
        self._wheel_radius_m = 0.0
        self._wheel_base_m = 0.0
        self._publish_rate_hz = 50.0

        self._load_parameters()
        self._initialize_gpio()

    def _get_parameter(self, name: str, default: Any) -> Any:
        if self._node is None:
            return default
        if not self._node.has_parameter(name):
            self._node.declare_parameter(name, default)
        return self._node.get_parameter(name).value

    @staticmethod
    def _is_configured(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return value.strip().upper() != 'TODO' and value.strip() != ''
        return True

    def _parse_float_parameter(self, name: str, default: float = 0.0) -> float:
        value = self._get_parameter(name, default)
        if not self._is_configured(value):
            return 0.0
        return float(value)

    def _load_parameters(self) -> None:
        self._left_gpio_a = self._get_parameter('encoders.left_gpio_a', 'TODO')
        self._left_gpio_b = self._get_parameter('encoders.left_gpio_b', 'TODO')
        self._right_gpio_a = self._get_parameter('encoders.right_gpio_a', 'TODO')
        self._right_gpio_b = self._get_parameter('encoders.right_gpio_b', 'TODO')
        self._ticks_per_revolution = self._parse_float_parameter(
            'encoders.ticks_per_revolution',
            0.0,
        )
        self._wheel_radius_m = self._parse_float_parameter(
            'encoders.wheel_radius_m',
            0.0,
        )
        self._wheel_base_m = self._parse_float_parameter(
            'encoders.wheel_base_m',
            0.0,
        )
        self._publish_rate_hz = self._parse_float_parameter(
            'encoders.publish_rate_hz',
            50.0,
        )

    def _initialize_gpio(self) -> None:
        pin_values = [
            self._left_gpio_a,
            self._left_gpio_b,
            self._right_gpio_a,
            self._right_gpio_b,
        ]
        pins_configured = all(self._is_configured(pin) for pin in pin_values)
        calibration_ready = (
            self._ticks_per_revolution > 0.0
            and self._wheel_radius_m > 0.0
            and self._wheel_base_m > 0.0
        )

        gpio_library = None
        try:
            import RPi.GPIO as GPIO  # noqa: F401
            gpio_library = 'RPi.GPIO'
        except ImportError:
            gpio_library = None

        if pins_configured and calibration_ready and gpio_library is not None:
            self._gpio_ready = False
            self._logger.warn(
                'TODO: JGB37-520 quadrature GPIO wiring is configured in parameters, '
                'but encoder interrupt handling is not implemented yet.'
            )
            return

        reasons = []
        if not pins_configured:
            reasons.append('GPIO pins are not configured')
        if not calibration_ready:
            reasons.append('encoder calibration parameters are not ready')
        if gpio_library is None:
            reasons.append('GPIO library is unavailable in this environment')

        self._gpio_ready = False
        self._logger.warn(
            'TODO: HardwareEncoder is not ready for JGB37-520 encoders: '
            + '; '.join(reasons)
        )

    def _now_sec(self) -> float:
        if self._node is not None:
            return self._node.get_clock().now().nanoseconds / 1e9
        return 0.0

    def _ticks_to_position_m(self, ticks: int) -> float:
        wheel_angle_rad = ticks * 2.0 * math.pi / self._ticks_per_revolution
        return wheel_angle_rad * self._wheel_radius_m

    def _ticks_to_velocity_mps(
        self,
        delta_ticks: int,
        delta_time_sec: float,
    ) -> float:
        if delta_time_sec <= 0.0:
            return 0.0

        wheel_angle_rad = delta_ticks * 2.0 * math.pi / self._ticks_per_revolution
        return (wheel_angle_rad * self._wheel_radius_m) / delta_time_sec

    def _zero_wheel_state(self) -> WheelState:
        msg = WheelState()
        msg.left_position = 0.0
        msg.right_position = 0.0
        msg.left_velocity = 0.0
        msg.right_velocity = 0.0
        return msg

    def _log_readiness_once(self) -> None:
        if self._readiness_logged:
            return
        self._readiness_logged = True
        self._logger.warn(
            'TODO: HardwareEncoder read() is returning zero WheelState until '
            'JGB37-520 GPIO quadrature support is implemented.'
        )

    def reset(self) -> None:
        self._left_ticks = 0
        self._right_ticks = 0
        self._previous_timestamp_sec = None
        self._previous_left_ticks = 0
        self._previous_right_ticks = 0

    def read(self) -> Optional[WheelState]:
        if not self._gpio_ready:
            self._log_readiness_once()
            return self._zero_wheel_state()

        now_sec = self._now_sec()
        if self._previous_timestamp_sec is None:
            self._previous_timestamp_sec = now_sec
            self._previous_left_ticks = self._left_ticks
            self._previous_right_ticks = self._right_ticks
            return self._zero_wheel_state()

        delta_time_sec = now_sec - self._previous_timestamp_sec
        delta_left_ticks = self._left_ticks - self._previous_left_ticks
        delta_right_ticks = self._right_ticks - self._previous_right_ticks

        msg = WheelState()
        msg.left_position = self._ticks_to_position_m(self._left_ticks)
        msg.right_position = self._ticks_to_position_m(self._right_ticks)
        msg.left_velocity = self._ticks_to_velocity_mps(delta_left_ticks, delta_time_sec)
        msg.right_velocity = self._ticks_to_velocity_mps(
            delta_right_ticks,
            delta_time_sec,
        )

        self._previous_timestamp_sec = now_sec
        self._previous_left_ticks = self._left_ticks
        self._previous_right_ticks = self._right_ticks
        return msg

    def close(self) -> None:
        self.reset()
