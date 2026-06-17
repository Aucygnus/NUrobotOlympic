import cv2
import mediapipe as mp
import urllib.request
import os
import pygame
import numpy as np

class PoseDetector:
    def __init__(self):
        self.modelPath = 'pose_landmarker.task'
        self.DownloadModel()
        
        options = mp.tasks.vision.PoseLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=self.modelPath),
            num_poses = 2,
            min_pose_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )
        self.landmarker = mp.tasks.vision.PoseLandmarker.create_from_options(options)
        
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    def DownloadModel(self):
        if not os.path.exists(self.modelPath):
            print("กำลังดาวน์โหลดโมเดล Pose...")
            urllib.request.urlretrieve(
                "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task", 
                self.modelPath
            )

    def ProcessFrame(self, width, height):
        success, img = self.cap.read()
        if not success:
            return None, (-1000, -1000), (-1000, -1000), (-1000, -1000)

        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mpimg = mp.Image(image_format=mp.ImageFormat.SRGB, data=imgRGB)
        result = self.landmarker.detect(mpimg)
        
        bg_surface = pygame.surfarray.make_surface(np.swapaxes(imgRGB, 0, 1))
        bg_surface = pygame.transform.scale(bg_surface, (width, height))

        nose = (-1000, -1000)
        LHand = (-1000, -1000)
        RHand = (-1000, -1000)
        
        if result.pose_landmarks:
            bestLandmarks = None
            minDist2Center = float('inf')
            screenCenterX = width // 2
            
            for landmarks in result.pose_landmarks:
                nose_x = int(landmarks[0].x * width)
                dist = abs(nose_x - screenCenterX)
                if dist < minDist2Center:
                    minDist2Center = dist
                    bestLandmarks = landmarks

            if bestLandmarks:
                nose = (int(bestLandmarks[0].x * width), int(bestLandmarks[0].y * height))
                LHand = (int(bestLandmarks[19].x * width), int(bestLandmarks[19].y * height))
                RHand = (int(bestLandmarks[20].x * width), int(bestLandmarks[20].y * height))

        return bg_surface, nose, LHand, RHand

    def release(self):
        self.cap.release()