# fakewebcam
Envoi d'images avec OpenCV sur une caméra virtuelle en python

![fakewebcam in VLC](color_depth.png?raw=true "Title")

## Creation d'une caméra virtuelle avec v4l2loopback

### Ce projet utlise une /dev/video11

### Installation
    sudo apt install v4l2loopback-utils v4l2loopback-dkms
    sudo modprobe v4l2loopback video_nr=11

Le device est détruit au reboot

### Extrait de la documentation v4l2loopback
[Documentation v4l2loopback](https://github.com/umlaeute/v4l2loopback)

Insert the v4l2loopback kernel module.

    sudo modprobe v4l2loopback devices=2

will create two fake webcam devices

You can also specify the device IDs manually; e.g.

    sudo modprobe v4l2loopback video_nr=3,4,7

Will create 3 devices (/dev/video3, /dev/video4 & /dev/video7)

Liste des devices existant

    sudo ls /dev/video*

retourne:

    /dev/video0  /dev/video1  /dev/video2  /dev/video3  /dev/video4  /dev/video5

### LOAD THE MODULE AT BOOT
Sources: https://askubuntu.com/questions/1245212/how-do-i-automatically-run-modprobe-v4l2loopback-on-boot

Valable pour Debian 11

    sudo echo "v4l2loopback" > /etc/modules-load.d/v4l2loopback.conf
    sudo echo "options v4l2loopback video_nr=11" > /etc/modprobe.d/v4l2loopback.conf
    sudo update-initramfs -c -k $(uname -r)

Reboot

### RealSense
#### Sans VirtualEnv

    python3 -m pip install numpy opencv-python pyfakewebcam pyrealsense2

Dans le dossier du projet, lancement du script:

    python3 sender_rs_depth.py

#### Avec VirtualEnv
Dans le dossier du projet:

    sudo apt install python3-venv
    python3 -m venv mon_env
    source mon_env/bin/activate
    python3 -m pip install numpy opencv-python pyfakewebcam pyrealsense2

Dans le dossier du projet, lancement du script

    ./mon_env/bin/python3 python3 sender_rs_depth.py

#### Utilisation: méthode un peu geek mais simple !
Au début du script:

* Changer le device si besoin le device VIDEO = '/dev/video11'
* SLIDER = 1 pour régler la profondeur. Une fenêtre avec un slider permet de régler la valeur de profondeur. Cette valeur n'est pas enregistrée. 
* Quand une valeur vous convient, modifier la valeur de CLIPPING_DISTANCE_IN_MILLIMETER et mettre SLIDER = 0. Il n'y aura plus d'affichage de fenêtre, seulement l'envoi visualisable dans VLC.

### OAK-D Lite de Luxonis
#### Sans VirtualEnv

    python3 -m pip install numpy opencv-python pyfakewebcam depthai

Dans le dossier du projet, lancement du script:

    python3 sender_oak_depth.py

#### Avec VirtualEnv
Dans le dossier du projet:

    sudo apt install python3-venv
    python3 -m venv mon_env
    source mon_env/bin/activate
    python3 -m pip install numpy opencv-python pyfakewebcam depthai

Dans le dossier du projet, lancement du script

    ./mon_env/bin/python3 python3 sender_oak_depth.py

![fakewebcam in VLC](oak_depth_in_vlc.png?raw=true "Title")