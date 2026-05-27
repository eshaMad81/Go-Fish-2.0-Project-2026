# Go-Fish-2.0-Project-2026

# How the Project Works

Go Fish 2.0 is an autonomous robotics system that uses computer vision to track a fish and command a robot to follow it in real time. The system consists of four major components: an overhead camera, a Raspberry Pi, a robot platform, and a LiDAR sensor.

First, an overhead webcam continuously captures video of the fish tank. The video feed is sent to a Raspberry Pi, which runs a Python program using OpenCV. Each frame is converted from BGR color space to HSV color space, which makes it easier to isolate the fish based on its color. A color threshold is applied to create a binary mask containing only pixels that match the fish's color.

Next, OpenCV identifies contours within the mask and selects the largest contour as the fish. The centroid of this contour is calculated using image moments. The centroid represents the fish's location within the frame.

The Raspberry Pi then compares the fish's centroid position to the center of the camera image:

Fish left of center → robot moves left
Fish right of center → robot moves right
Fish above center → robot moves forward
Fish below center → robot moves backward

The difference between the fish location and the frame center is used to calculate movement velocities. These velocities are intentionally limited to low values to produce smoother robot movement and prevent sudden turns.

Once the movement commands are generated, the Raspberry Pi sends them through a USB serial connection to the VEX V5 Brain. The VEX Brain receives the motor commands and controls the drive motors accordingly.

At the same time, an RPLIDAR sensor continuously scans the robot's surroundings. If an obstacle is detected, the system can prevent forward movement and initiate avoidance behavior. This allows the robot to navigate within a maze environment without colliding with walls.

A Flask web server running on the Raspberry Pi streams the camera feed to a laptop. The web interface displays: The raw camera feed, The HSV tracking visualization, The fish contour, The centroid position, dx and dy values

#How to Replicate the Project

Hardware: Raspberry Pi, MicroSD card with Raspberry Pi OS, USB Webcam, VEX V5 Brain, VEX Drive Motors, Robot chassis, RPLIDAR A1M8, USB cables, Power source for Raspberry Pi and VEX, Software, Python 3, OpenCV, NumPy, Flask, PySerial, VEXcode, Python

**Setup Instructions**

**Step 1: Raspberry Pi Setup**

Begin by installing Raspberry Pi OS on a microSD card and booting the Raspberry Pi. Connect the Raspberry Pi to a network using either Ethernet or Wi-Fi and enable SSH access for remote development through enabling Internet Sharing. Once connected, update the operating system and install the required Python libraries and packages used throughout the project.

commands: 

sudo apt update
sudo apt upgrade

sudo apt install python3-opencv
sudo apt install python3-flask
sudo apt install python3-serial
sudo apt install python3-pip

**Step 2: Camera Setup**

Connect a USB webcam to the Raspberry Pi. Verify that the camera is detected by the operating system:

lsusb

The camera should appear in the device list. Next, verify that a video device has been created:

ls /dev/video*

A successful setup should show a device such as:

/dev/video0

Capture a test image to ensure the camera is functioning correctly:

sudo apt install fswebcam
fswebcam test.jpg

If the image is successfully captured, the camera is ready for use with the HSV tracking system.

**Step 3: Install Project Dependencies**

The project relies on several Python libraries for computer vision, web streaming, and serial communication.

Install any remaining dependencies:

pip3 install numpy

The primary libraries used in this project are: OpenCV, NumPy, Flask, PySerial

**Step 4: VEX V5 Setup

Assemble the robot chassis and connect the drive motors to the VEX V5 Brain.

Motor configuration used in this project:

Motor	Port: 
-   Left Drive Motor	Port 1
-   Right Drive Motor	Port 10

Upload a test program to verify that both motors can move forward, backward, left, and right before integrating the Raspberry Pi.

vexTest.py is a file included in this git, so that can be used as the test file.
[add how to download]

**Step 5: Connect Raspberry Pi to VEX Brain

Connect the Raspberry Pi to the VEX V5 Brain using a USB data cable.

Verify that the VEX Brain is recognized by the Raspberry Pi:

ls /dev/tty*

The VEX Brain should appear as a serial device such as:

/dev/ttyACM0

This serial connection allows the Raspberry Pi to transmit movement commands generated from the HSV tracking system directly to the robot.

**Step 6: LiDAR Setup

Connect the RPLIDAR A1M8 to the Raspberry Pi using USB.

Verify detection:

lsusb

Install the required LiDAR library:

pip3 install rplidar-roboticia

The LiDAR continuously scans the robot's surroundings and can be used for obstacle detection and maze navigation.

**Step 7: Running the HSV Tracking System

Launch the HSV tracking server:

python3 fish_server.py

The program performs the following tasks simultaneously:

- Captures video from the overhead webcam.
- Detects the fish using HSV color segmentation.
- Calculates the fish centroid position.
- Computes robot movement commands.
- Sends commands to the VEX V5 Brain.
- Streams the live tracking feed through a web server.

Find the Raspberry Pi IP address:

hostname -I

Open a web browser on a laptop and navigate to:

http://<PI_IP>:5000

The interface displays:
- HSV tracking visualization
- Fish contour and centroid
- Position offsets (dx, dy)
- Calculated motor commands
- Raw camera feed

**Step 8: Testing the System

Place the fish target inside the tank and position the overhead camera above the workspace. For testing purposes, the fish can be moved manually or with a magnet underneath the tank.

As the fish moves:

Left → Robot moves left
Right → Robot moves right
Up → Robot moves forward
Down → Robot moves backward

The robot should respond smoothly using velocity-based control while the live web interface displays all tracking calculations in real time.



