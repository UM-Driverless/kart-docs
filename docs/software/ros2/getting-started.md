# Getting Started

The kart software runs on **Ubuntu 22.04** with **ROS 2 Humble**. There are two deployment targets:

| | Simulation (development) | Real Hardware (on the kart) |
|---|---|---|
| **Machine** | Mac → UTM VM (Ubuntu 22.04 ARM64) | Jetson AGX Orin (Ubuntu 22.04 ARM64) |
| **Sensor** | Gazebo Fortress simulated RGBD camera | ZED stereo camera |
| **Perception** | Ground truth from SDF, or YOLO on simulated images | YOLO + depth projection |
| **Actuators** | Gazebo Ackermann plugin (`/kart/cmd_vel`) | ESP32 over USB serial (`/kart/cmd_vel` → `state_machine` → `/kart/cmd_vel_muxed` → `cmd_vel_bridge` → framed int32 protocol) |
| **GPU** | None (LLVMpipe software rendering) | NVIDIA GPU (CUDA for YOLO + ZED) |

Both targets produce the same `/perception/cones_3d` topic — a controller node works identically in either mode.

---

## 1. Simulation on Mac (via UTM VM)

### Prerequisites

Set up a UTM virtual machine running Ubuntu 22.04 ARM64 with at least 8 GB RAM and 4 CPU cores. Configure SSH access so you can reach it with `ssh utm` (or use the IP directly, typically `192.168.65.2`).

On the VM, install ROS 2 Humble:

```bash
# Follow https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html
sudo apt install ros-humble-desktop
```

Install simulation dependencies:

```bash
sudo apt install \
  ros-humble-ros-gz \
  ros-humble-vision-msgs \
  ros-humble-xacro \
  ros-humble-tf2-ros \
  mesa-utils libegl1-mesa-dev libgles2-mesa-dev
```

`ros-humble-ros-gz` installs Gazebo Fortress and the ROS bridge (~3-4 GB).

### Clone & Build

```bash
ssh utm

cd ~
git clone https://github.com/UM-Driverless/kart-brain.git
source /opt/ros/humble/setup.bash
cd ~/kart-brain
colcon build
source install/setup.bash
```

!!! tip "Add to `.bashrc` for convenience"
    ```bash
    echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc
    echo 'source ~/kart-brain/install/setup.bash 2>/dev/null' >> ~/.bashrc
    echo 'export IGN_GAZEBO_RESOURCE_PATH=$(ros2 pkg prefix kart_sim 2>/dev/null)/share/kart_sim/models' >> ~/.bashrc
    ```

### Launch the Simulation

```bash
# Default: ground-truth perception (no YOLO, no camera needed)
ros2 launch kart_sim simulation.launch.py

# With YOLO vision pipeline (uses simulated camera images)
ros2 launch kart_sim simulation.launch.py use_yolo:=true
```

Default mode launches 5 processes:

1. **Gazebo server** — headless physics + OGRE2 rendering (LLVMpipe)
2. **ros_gz_bridge** — bridges Gazebo topics to ROS 2
3. **perfect_perception_node** — ground-truth cone detection from SDF
4. **cone_marker_viz_3d** — RViz marker visualization
5. **cone_follower_node** — midpoint-steering controller

With `use_yolo:=true`, it replaces perfect perception with:

- **camera_info_fix_node** — corrects Gazebo's wrong camera intrinsics
- **yolo_detector** — YOLOv11 inference on simulated images
- **cone_depth_localizer** — depth-based 2D→3D projection

### Verify it's working

In a second SSH terminal:

```bash
ssh utm

source /opt/ros/humble/setup.bash
source ~/kart-brain/install/setup.bash

# Check topics are active
ros2 topic list

# See cone detections
ros2 topic echo /perception/cones_3d --once

# See controller output
ros2 topic echo /kart/cmd_vel --once
```

### Visualize

**RViz** (via X11 forwarding):

```bash
ssh -X utm
rviz2
```

1. Set **Fixed Frame** to `odom`
2. Add **MarkerArray** → `/perception/cones_3d_markers`
3. Add **TF** to see the kart's position
4. Add **Odometry** → `/model/kart/odometry` for velocity arrows

**Foxglove Studio** (from Mac — best experience):

```bash
# On the VM
sudo apt install ros-humble-rosbridge-server
ros2 launch rosbridge_server rosbridge_websocket_launch.xml

# On Mac: open Foxglove Studio, connect to ws://192.168.65.2:9090
```

See [Simulation](simulation.md) for track layout, kart model specs, and troubleshooting.

---

## 2. Real Hardware on the Jetson Orin

### Prerequisites

Follow the **[Orin Setup Guide](../../assembly/electronics/orin-setup.md)** to flash the Orin and install all software (JetPack, CUDA, ROS 2, ZED SDK, PyTorch, kart-brain, remote access). That guide covers everything from a blank Orin to a fully configured system.

Once setup is complete, the kart-brain workspace is already built at `~/kart-brain`.

### Connect Hardware

Before launching, connect:

1. **ZED camera** — USB 3.0 port
2. **ESP32 (Kart Medulla)** — connect the Orin to the ESP32-S3 DevKitC-1 USB-C connector marked **`COM`**. It carries the UART command and telemetry link through the WCH CH343 bridge. The other connector, marked `USB`, is native USB debug and does not carry kart protocol frames. The Orin's persistent device path is `/dev/serial/by-id/usb-1a86_USB_Single_Serial_5C37207028-if00` (also commonly `/dev/ttyACM0`); the retired classic board used `/dev/ttyUSB0`.
3. **Gamepad** — USB or Bluetooth

If ESP32 telemetry is missing, first check the cable is in `COM`, then check that the persistent device path exists on the Orin. Seeing boot logs on the `USB` connector does not confirm that the kart command and telemetry link is connected.

### Manual Driving (Teleop)

```bash
ros2 launch kart_bringup teleop.launch.py
```

Hold **R1** (deadman switch) and use **R2** for throttle, **L2** for brake, **left stick** for steering.

### Autonomous Perception

Start the ZED camera node, then launch the perception pipeline:

```bash
# Terminal 1: ZED camera
ros2 launch zed_wrapper zed_camera.launch.py camera_model:=zed2

# Terminal 2: Perception pipeline
ros2 launch kart_perception perception_3d.launch.py
```

This runs YOLO detection, depth-based 3D localization, and RViz visualization. The ZED provides correct camera intrinsics natively — no fix node needed (that's simulation-only).

Verify detections:

```bash
ros2 topic echo /perception/cones_3d --once
```

### Full Autonomous Stack

Once perception is running, start a controller node that subscribes to `/perception/cones_3d` and publishes `Twist` on `/kart/cmd_vel`. The `cone_follower_node` from kart_control does exactly this — it works identically in simulation and on real hardware.

---

## Rebuilding After Changes

```bash
# Rebuild everything (--symlink-install so Python/launch edits work without rebuilding)
cd ~/kart-brain && colcon build --symlink-install && source install/setup.bash

# Rebuild only the package you changed (faster)
colcon build --symlink-install --packages-select kart_sim && source install/setup.bash
```

!!! tip "Why `--symlink-install`?"
    With `--symlink-install`, Python scripts and launch files in `install/` are symlinks to `src/`. Edits take effect immediately — only C++ changes need a rebuild. **Always use this flag.**

!!! warning "Always re-source after building"
    After `colcon build`, you must run `source install/setup.bash` for the changes to take effect in your current terminal. New terminals that source it from `.bashrc` pick it up automatically.

## Useful Commands

```bash
# List all active topics
ros2 topic list

# See message rate
ros2 topic hz /perception/cones_3d

# Echo a topic (one message)
ros2 topic echo /kart/cmd_vel --once

# Publish a manual velocity command (simulation only)
ros2 topic pub /kart/cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 2.0}, angular: {z: 0.0}}" -r 10

# List running nodes
ros2 node list

# Stop the simulation
pkill -9 ign; pkill -f parameter_bridge; pkill -f perfect_perception; pkill -f cone_follower
```
