# Docker ROS2 Jazzy Development Setup

This project includes a Docker-based ROS2 Jazzy development environment for Windows.

The container runs Ubuntu 24.04 with ROS2 Jazzy installed from:

```bash
osrf/ros:jazzy-desktop
```

Your local `ros2_ws` folder is mounted into the container at:

```bash
/ros2_ws
```

The container also mounts the full project folder at:

```bash
/project
```

## Build the Container

From the repository root, run:

```bash
docker compose build
```

## Start the Container

Start the container in the background:

```bash
docker compose up -d
```

The container name is:

```bash
ros2_jazzy_dev
```

## Enter the Container

Open an interactive shell:

```bash
docker exec -it ros2_jazzy_dev bash
```

The shell starts in:

```bash
/ros2_ws
```

ROS2 Jazzy is sourced automatically when you open a shell:

```bash
source /opt/ros/jazzy/setup.bash
```

If the workspace has already been built, this is sourced automatically too:

```bash
source /ros2_ws/install/setup.bash
```

## Check ROS2 Is Working

Inside the container, run:

```bash
ros2 --version
```

You can also list available ROS2 commands:

```bash
ros2 --help
```

## Create a ROS2 Package

Inside the container, go to the workspace source folder:

```bash
cd /ros2_ws/src
```

Create a Python package:

```bash
ros2 pkg create --build-type ament_python balance_robot
```

Or create a C++ package:

```bash
ros2 pkg create --build-type ament_cmake balance_robot
```

If the `balance_robot` package folder already exists, do not run the package creation command again with the same name.

## Build the Workspace

From inside the container:

```bash
cd /ros2_ws
colcon build
```

Build output is written to:

```bash
/ros2_ws/build
/ros2_ws/install
/ros2_ws/log
```

These folders are generated files and should not be committed to git.

## Source the Workspace

After building, source the workspace:

```bash
source /ros2_ws/install/setup.bash
```

New interactive shells source this file automatically if it exists.

## Stop the Container

From the repository root on Windows, run:

```bash
docker compose down
```

To start it again later:

```bash
docker compose up -d
```
