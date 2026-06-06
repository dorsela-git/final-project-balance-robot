cmake_minimum_required(VERSION 3.8)
project(balance_robot)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rosidl_default_generators REQUIRED)

ament_get_python_install_dir(PYTHON_INSTALL_DIR)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/RobotState.msg"
  "msg/WheelState.msg"
  "msg/MotorCommand.msg"
  "msg/SystemStatus.msg"
)

install(DIRECTORY
  ${PROJECT_NAME}/
  DESTINATION ${PYTHON_INSTALL_DIR}/${PROJECT_NAME}
  PATTERN "__pycache__" EXCLUDE
)

install(PROGRAMS
  scripts/imu_node
  scripts/encoder_node
  scripts/state_estimator_node
  scripts/lqr_controller_node
  scripts/motor_node
  scripts/diagnostics_node
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY
  launch
  config
  DESTINATION share/${PROJECT_NAME}
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
