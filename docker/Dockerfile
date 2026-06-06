FROM osrf/ros:jazzy-desktop

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    nano \
    python3-colcon-common-extensions \
    python3-pip \
    python3-rosdep \
    vim \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /ros2_ws/src

RUN echo "source /opt/ros/jazzy/setup.bash" >> /root/.bashrc \
    && echo "if [ -f /ros2_ws/install/setup.bash ]; then source /ros2_ws/install/setup.bash; fi" >> /root/.bashrc

WORKDIR /ros2_ws

CMD ["bash"]
