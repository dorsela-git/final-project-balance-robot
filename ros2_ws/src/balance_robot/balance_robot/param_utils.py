"""ROS 2 parameter helpers for nodes loaded from robot_params.yaml."""

from typing import Any

NODE_PARAM_AUTO_DECLARE = {
    'automatically_declare_parameters_from_overrides': True,
}


def get_param_or_default(node, name: str, default: Any) -> Any:
    if node.has_parameter(name):
        return node.get_parameter(name).value
    return default
