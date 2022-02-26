
"""
Créer un device /dev/video11
Commande non persistante, c'est perdu au reboot

sudo modprobe v4l2loopback video_nr=11


Sans VirtualEnv

    python3 -m pip install numpy opencv-python pyfakewebcam

    Lancement du script, dans le dossier du script

    python3 cam_relay.py

Avec VirtualEnv

    Dans le dossier du projet:

    python3 -m venv mon_env
    source mon_env/bin/activate
    python3 -m pip install numpy opencv-python pyfakewebcam

    Lancement du script, dans le dossier du script

    ./mon_env/bin/python3 python3 cam_relay.py

"""

import pyfakewebcam
import cv2
import numpy as np

cap = cv2.VideoCapture(0)
camera = pyfakewebcam.FakeWebcam('/dev/video11', 640, 480)

while True:
    ret, image = cap.read()
    if ret:
        # # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        camera.schedule_frame(image)
    if cv2.waitKey(1) == 27:
        break

"""
Run the following command to see the output of the fake webcam.

ffplay /dev/video11
or open the camera 11 in vlc
"""
