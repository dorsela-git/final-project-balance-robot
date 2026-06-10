import math
from typing import Any, Optional

from balance_robot.msg import WheelState

from balance_robot.hal.base_encoder import BaseEncoder


class HardwareEncoder(BaseEncoder):
    """JGB37-520 Hall quadrature encoder for Raspberry Pi GPIO via gpiozero."""

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

        self._left_encoder = None
        self._right_encoder = None
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
            return default
        return self._node.get_parameter(name).value

    @staticmethod
    def _is_configured(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return value.strip().upper() != 'TODO' and value.strip() != ''
        if isinstance(value, (int, float)):
            return int(value) >= 0
        return True

    @staticmethod
    def _parse_gpio_pin(value: Any) -> Optional[int]:
        if not HardwareEncoder._is_configured(value):
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        pin_text = str(value).strip().upper()
        if pin_text.startswith('GPIO'):
            pin_text = pin_text[4:]
        return int(pin_text)

    def _parse_float_parameter(self, name: str, default: float = 0.0) -> float:
        value = self._get_parameter(name, default)
        if not self._is_configured(value):
            return 0.0
        return float(value)

    def _load_parameters(self) -> None:
        self._left_gpio_a = self._get_parameter('encoders.left_gpio_a', -1)
        self._left_gpio_b = self._get_parameter('encoders.left_gpio_b', -1)
        self._right_gpio_a = self._get_parameter('encoders.right_gpio_a', -1)
        self._right_gpio_b = self._get_parameter('encoders.right_gpio_b', -1)
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

    def _left_pins_configured(self) -> bool:
        return (
            self._is_configured(self._left_gpio_a)
            and self._is_configured(self._left_gpio_b)
        )

    def _right_pins_configured(self) -> bool:
        return (
            self._is_configured(self._right_gpio_a)
            and self._is_configured(self._right_gpio_b)
        )

    def _calibration_ready(self) -> bool:
        return self._ticks_per_revolution > 0.0 and self._wheel_radius_m > 0.0

    def _initialize_gpio(self) -> None:
        left_ready = self._left_pins_configured() and self._calibration_ready()
        if not left_ready:
            reasons = []
            if not self._left_pins_configured():
                reasons.append('left encoder GPIO pins are not configured')
            if not self._calibration_ready():
                reasons.append(
                    'encoder calibration parameters are not ready '
                    '(ticks_per_revolution and wheel_radius_m required)'
                )
            self._gpio_ready = False
            self._logger.warn(
                'HardwareEncoder is not ready for JGB37-520 encoders: '
                + '; '.join(reasons)
            )
            return

        try:
            from gpiozero import RotaryEncoder
        except ImportError:
            self._gpio_ready = False
            self._logger.warn(
                'HardwareEncoder is not ready for JGB37-520 encoders: '
                'gpiozero is unavailable in this environment'
            )
            return

        left_pin_a = self._parse_gpio_pin(self._left_gpio_a)
        left_pin_b = self._parse_gpio_pin(self._left_gpio_b)
        if left_pin_a is None or left_pin_b is None:
            self._gpio_ready = False
            self._logger.warn(
                'HardwareEncoder is not ready for JGB37-520 encoders: '
                'left encoder GPIO pins could not be parsed'
            )
            return

        try:
            self._left_encoder = RotaryEncoder(left_pin_a, left_pin_b, max_steps=0)
        except Exception as exc:
            self._gpio_ready = False
            self._logger.warn(
                'HardwareEncoder failed to initialize left encoder on '
                f'GPIO{left_pin_a}/GPIO{left_pin_b}: {exc}'
            )
            return

        self._gpio_ready = True
        mode = 'left-only'
        if self._right_pins_configured():
            right_pin_a = self._parse_gpio_pin(self._right_gpio_a)
            right_pin_b = self._parse_gpio_pin(self._right_gpio_b)
            if right_pin_a is not None and right_pin_b is not None:
                try:
                    self._right_encoder = RotaryEncoder(
                        right_pin_a,
                        right_pin_b,
                        max_steps=0,
                    )
                    mode = 'left and right'
                except Exception as exc:
                    self._logger.warn(
                        'Right encoder GPIO pins are configured but initialization '
                        f'failed; right wheel will remain zero: {exc}'
                    )
        else:
            self._logger.info(
                'Right encoder pins are not configured; right wheel fields will '
                'remain zero.'
            )

        self._logger.info(
            'HardwareEncoder ready in '
            f'{mode} mode: left GPIO{left_pin_a}/GPIO{left_pin_b}, '
            f'ticks_per_revolution={self._ticks_per_revolution:.0f}, '
            f'wheel_radius_m={self._wheel_radius_m:.3f}'
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
            'HardwareEncoder read() is returning zero WheelState because GPIO '
            'initialization did not succeed.'
        )

    def _sample_ticks(self) -> None:
        if self._left_encoder is not None:
            # Forward wheel rotation should increase left_position.
            self._left_ticks = self._left_encoder.steps
        if self._right_encoder is not None:
            self._right_ticks = self._right_encoder.steps
        else:
            self._right_ticks = 0

    def _reset_encoder_devices(self) -> None:
        if self._left_encoder is not None:
            self._left_encoder.steps = 0
        if self._right_encoder is not None:
            self._right_encoder.steps = 0

    def reset(self) -> None:
        self._left_ticks = 0
        self._right_ticks = 0
        self._previous_timestamp_sec = None
        self._previous_left_ticks = 0
        self._previous_right_ticks = 0
        if self._gpio_ready:
            self._reset_encoder_devices()

    def read(self) -> Optional[WheelState]:
        if not self._gpio_ready:
            self._log_readiness_once()
            return self._zero_wheel_state()

        self._sample_ticks()

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
        if self._left_encoder is not None:
            self._left_encoder.close()
            self._left_encoder = None
        if self._right_encoder is not None:
            self._right_encoder.close()
            self._right_encoder = None
        self.reset()
