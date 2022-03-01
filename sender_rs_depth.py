
"""
Voir https://github.com/sergeLabo/fakewebcam

Suppression du fond, voir
https://github.com/IntelRealSense/librealsense/blob/master/wrappers/python/examples/align-depth2color.py
"""

import os
import time
import pyfakewebcam
import cv2
import numpy as np
import pyrealsense2 as rs


# Le faux device
VIDEO = '/dev/video11'

# Avec ou sans slider pour régler CLIPPING_DISTANCE_IN_MILLIMETER
SLIDER = 1
# Réglable avec le slider
# We will be removing the background of objects more than
# CLIPPING_DISTANCE_IN_MILLIMETER away
CLIPPING_DISTANCE_IN_MILLIMETER = 2000


class MyRealSense:

    def __init__(self, video, slider, clip):
        self.video = video
        self.slider = slider
        self.clip = clip

        self.width = 1280
        self.height = 720
        self.pose_loop = 1
        self.pipeline = rs.pipeline()
        config = rs.config()
        pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        try:
            pipeline_profile = config.resolve(pipeline_wrapper)
        except:
            print('\n\nPas de Capteur Realsense connecté\n\n')
            os._exit(0)
        device = pipeline_profile.get_device()
        config.enable_stream(   rs.stream.color,
                                width=self.width,
                                height=self.height,
                                format=rs.format.bgr8,
                                framerate=30)
        config.enable_stream(   rs.stream.depth,
                                width=self.width,
                                height=self.height,
                                format=rs.format.z16,
                                framerate=30)

        profile = self.pipeline.start(config)
        self.align = rs.align(rs.stream.color)
        unaligned_frames = self.pipeline.wait_for_frames()
        frames = self.align.process(unaligned_frames)

        # Getting the depth sensor's depth scale (see rs-align example for explanation)
        depth_sensor = profile.get_device().first_depth_sensor()
        self.depth_scale = depth_sensor.get_depth_scale()
        print("Depth Scale is: " , self.depth_scale)

        # Affichage de la taille des images
        color_frame = frames.get_color_frame()
        img = np.asanyarray(color_frame.get_data())
        print(f"Taille des images:"
              f"     {img.shape[1]}x{img.shape[0]}")

        self.camera = pyfakewebcam.FakeWebcam(VIDEO, 1280, 720)

        if self.slider:
            self.create_slider()

    def create_slider(self):
        cv2.namedWindow('controls')
        cv2.createTrackbar('background', 'controls', 1000, 8000,
                            self.remove_background_callback)
        cv2.setTrackbarPos('background', 'controls', self.clip)
        cv2.namedWindow('depth', cv2.WND_PROP_FULLSCREEN)

    def remove_background_callback(self, value):
        if value != 1000:
            self.clip = int(value)

    def run(self):
        """Boucle infinie, quitter avec Echap dans la fenêtre OpenCV"""

        while self.pose_loop:

            # Get frameset of color and depth
            frames = self.pipeline.wait_for_frames()
            # frames.get_depth_frame() is a 640x360 depth image

            # Align the depth frame to color frame
            aligned_frames = self.align.process(frames)

            # aligned_depth_frame is a 640x480 depth image
            aligned_depth_frame = aligned_frames.get_depth_frame()
            color_frame = aligned_frames.get_color_frame()

            # Validate that both frames are valid
            if not aligned_depth_frame or not color_frame:
                continue

            depth_image = np.asanyarray(aligned_depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            # Remove background - Set pixels further than clipping_distance to grey
            # depth image is 1 channel, color is 3 channels
            depth_image_3d = np.dstack((depth_image, depth_image, depth_image))
            clipping_distance = self.clip / (1000*self.depth_scale)
            bg_removed = np.where((depth_image_3d > clipping_distance) |\
                        (depth_image_3d <= 0), 0, color_image)

            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image,
                                                                   alpha=0.03),
                                                                   cv2.COLORMAP_JET)
            images = np.hstack((bg_removed, depth_colormap))

            if self.slider:
                cv2.imshow('depth', images)

            self.camera.schedule_frame(bg_removed)

            if cv2.waitKey(1) == 27:
                break



if __name__ == '__main__':

    mrs = MyRealSense(VIDEO, SLIDER, CLIPPING_DISTANCE_IN_MILLIMETER)
    mrs.run()
