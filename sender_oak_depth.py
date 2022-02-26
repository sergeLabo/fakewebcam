"""
Créer un device /dev/video11
Commande non persistante, c'est perdu au reboot

sudo modprobe v4l2loopback video_nr=11

Necéssite depthai

Sans VirtualEnv

    python3 -m pip install numpy opencv-python pyfakewebcam depthai

    Lancement du script, dans le dossier du script

    python3 sender_oak_depth.py

Avec VirtualEnv

    Dans le dossier du projet:

    python3 -m venv mon_env
    source mon_env/bin/activate
    python3 -m pip install numpy opencv-python pyfakewebcam depthai

    Lancement du script, dans le dossier du script

    ./mon_env/bin/python3 python3 sender_oak_depth.py

"""


import cv2
import depthai as dai
import numpy as np
import pyfakewebcam


pipeline = dai.Pipeline()

# Define a source - two mono (grayscale) cameras
left = pipeline.createMonoCamera()
left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
left.setBoardSocket(dai.CameraBoardSocket.LEFT)

right = pipeline.createMonoCamera()
right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
right.setBoardSocket(dai.CameraBoardSocket.RIGHT)

# Create a node that will produce the depth map
# (using disparity output as it's easier to visualize depth this way)
depth = pipeline.createStereoDepth()
depth.setConfidenceThreshold(200)

# Options: MEDIAN_OFF, KERNEL_3x3, KERNEL_5x5, KERNEL_7x7 (default)
median = dai.StereoDepthProperties.MedianFilter.KERNEL_7x7 # For depth filtering
depth.setMedianFilter(median)

# Better handling for occlusions:
depth.setLeftRightCheck(False)
# Closer-in minimum depth, disparity range is doubled:
depth.setExtendedDisparity(False)
# Better accuracy for longer distance, fractional disparity 32-levels:
depth.setSubpixel(False)

left.out.link(depth.left)
right.out.link(depth.right)

# Create output
xout = pipeline.createXLinkOut()
xout.setStreamName("disparity")
depth.disparity.link(xout.input)

camera = pyfakewebcam.FakeWebcam('/dev/video11', 640, 480)

with dai.Device(pipeline) as device:
    device.startPipeline()

    # Output queue will be used to get the disparity frames from the outputs defined above
    q = device.getOutputQueue(name="disparity", maxSize=4, blocking=False)

    while True:
        inDepth = q.get()  # blocking call, will wait until a new data has arrived
        frame = inDepth.getFrame()
        frame = cv2.normalize(frame, None, 0, 255, cv2.NORM_MINMAX)

        depth_gray_image = cv2.resize(np.asanyarray(frame), (640, 480),
                                interpolation = cv2.INTER_AREA)
        # v4l2 doit être RGB
        color = cv2.cvtColor(depth_gray_image, cv2.COLOR_GRAY2RGB)
        camera.schedule_frame(color)

        if cv2.waitKey(1) == 27:
            break
