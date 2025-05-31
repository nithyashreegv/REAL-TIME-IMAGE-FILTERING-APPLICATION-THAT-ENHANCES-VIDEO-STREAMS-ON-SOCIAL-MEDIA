
'''

import cv2
import mediapipe as mp
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading



class VideoProcessor:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Webcam not accessible")
            raise ValueError("Webcam not accessible")

        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(max_num_faces=1, min_detection_confidence=0.5)

        # Load filters
        self.filters = {
            "none": None,
            "hat": cv2.imread("hat.jpg", -1),
            "mustache": cv2.imread("mustache.jpg", -1),
            "flower_crown":cv2.imread("flower_crown.png",-1),
            "sunglass":cv2.imread("sunglass.png",-1),
            "bread":cv2.imread("beard.png",-1)
        }
        self.current_filter = "none"

    def overlay_filter(self, frame, filter_img, x, y, w, h, is_mustache=False):
        if filter_img is None:
            return frame
        
        filt_h, filt_w = filter_img.shape[:2]
        filt_resized = cv2.resize(filter_img, (w, int(filt_h * w / filt_w)))

        y_offset = y + int(h * 2 / 3) if is_mustache else y - filt_resized.shape[0]
        y_offset = max(y_offset, 0)

        has_alpha = filt_resized.shape[2] == 4

        for i in range(filt_resized.shape[0]):
            for j in range(filt_resized.shape[1]):
                if y_offset + i >= frame.shape[0] or x + j >= frame.shape[1]:
                    continue
                if has_alpha and filt_resized[i, j, 3] != 0:
                    frame[y_offset + i, x + j] = filt_resized[i, j, :3]
                elif not has_alpha:
                    frame[y_offset + i, x + j] = filt_resized[i, j]
        return frame

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Webcam fail!")
            return None

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame_rgb)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                h, w, _ = frame.shape
                x_min = min([lm.x for lm in face_landmarks.landmark]) * w
                x_max = max([lm.x for lm in face_landmarks.landmark]) * w
                y_min = min([lm.y for lm in face_landmarks.landmark]) * h
                y_max = max([lm.y for lm in face_landmarks.landmark]) * h

                x, y = int(x_min), int(y_min)
                fw, fh = int(x_max - x_min), int(y_max - y_min)
                is_mustache = self.current_filter == "mustache"

                frame = self.overlay_filter(frame, self.filters[self.current_filter], x, y, fw, fh, is_mustache)

        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def set_filter(self, filter_name):
        if filter_name in self.filters:
            print(f"Setting filter: {filter_name}")
            self.current_filter = filter_name

    def release(self):
        self.cap.release()

class VideoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Filter App")
        self.video_processor = VideoProcessor()

        # UI Components
        self.canvas = tk.Canvas(root, width=1100, height=1100)
        self.canvas.pack()

        self.filter_label = tk.Label(root, text="Choose a Filter:")
        self.filter_label.pack()

        self.filter_var = tk.StringVar(value="none")
        self.filter_menu = ttk.Combobox(root, textvariable=self.filter_var, values=list(self.video_processor.filters.keys()), state="readonly")
        self.filter_menu.pack()
        self.filter_menu.bind("<<ComboboxSelected>>", self.update_filter)

        self.quit_button = tk.Button(root, text="Quit", command=self.quit_app)
        self.quit_button.pack()

        self.update_video()
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

    def update_filter(self, event):
        selected_filter = self.filter_var.get()
        self.video_processor.set_filter(selected_filter)

    def update_video(self):
        frame = self.video_processor.get_frame()
        if frame is not None:
            frame = Image.fromarray(frame)
            frame = ImageTk.PhotoImage(frame)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=frame)
            self.canvas.image = frame
        self.root.after(10, self.update_video)

    def quit_app(self):
        self.video_processor.release()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoApp(root)
    root.mainloop()

'''
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class VideoProcessor:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Webcam not accessible")
            raise ValueError("Webcam not accessible")
        
        # Load Haar cascade for face detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

        # Load filters
        self.filters = {
            "none": None,
            "hat": cv2.imread("hat.jpg", -1),
            "mustache": cv2.imread("mustache.jpg", -1),
            "flower_crown": cv2.imread("flower_crown.png", -1),
            "sunglass": cv2.imread("sunglass.png", -1),
            "beard": cv2.imread("beard.png", -1),
            "butterfly":cv2.imread("butterfly.png",-1)
        }
        self.current_filter = "none"
    
    def overlay_filter(self, frame, filter_img, x, y, w, h, current_filter_key):
        if filter_img is None:
            return frame
        
        filt_h, filt_w = filter_img.shape[:2]
        scale_factor = w / filt_w
        filt_resized = cv2.resize(filter_img, (w, int(filt_h * scale_factor)))

        

        if current_filter_key == "mustache":
            y_offset = y + int(h / 1.5)
            x_offset = x + int(w / 4)
            w = int(w / 2)
            h = int(h / 6)
        elif current_filter_key == "flower_crown":
            y_offset = y - int(h * 0.2)
            y_offset = max(0, y_offset)
            x_offset = x - int(w * 0.1)
            w = int(w * 1.2)
            h = int(h * 0.4)

        elif current_filter_key == "butterfly":
            y_offset = y - int(h * 0.2)
            y_offset = max(0, y_offset)
            x_offset = x - int(w * 0.1)
            w = int(w * 1.2)
            h = int(h * 0.4)

        elif current_filter_key == "beard":
            y_offset = y + int(h * 0.75)
            x_offset = x + int(w * 0.25)
            w = int(w * 0.5)
            h = int(h * 0.3)
        else:
            y_offset = y - filt_resized.shape[0] // 2
            x_offset = x

        y_offset = max(y_offset, 0)
        
        for i in range(filt_resized.shape[0]):
            for j in range(filt_resized.shape[1]):
                if y_offset + i >= frame.shape[0] or x_offset + j >= frame.shape[1]:
                    continue
                alpha = filt_resized[i, j, 3] / 255.0 if filt_resized.shape[2] == 4 else 1.0
                frame[y_offset + i, x_offset + j] = (1 - alpha) * frame[y_offset + i, x_offset + j] + alpha * filt_resized[i, j, :3]
        return frame
    
    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Webcam fail!")
            return None
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            frame = self.overlay_filter(frame, self.filters[self.current_filter], x, y, w, h, self.current_filter)

        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    def set_filter(self, filter_name):
        if filter_name in self.filters:
            print(f"Setting filter: {filter_name}")
            self.current_filter = filter_name
    
    def release(self):
        self.cap.release()

class VideoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Filter App")
        self.video_processor = VideoProcessor()

        # UI Components
        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack()

        self.filter_label = tk.Label(root, text="Choose a Filter:")
        self.filter_label.pack()

        self.filter_var = tk.StringVar(value="none")
        self.filter_menu = ttk.Combobox(root, textvariable=self.filter_var, values=list(self.video_processor.filters.keys()), state="readonly")
        self.filter_menu.pack()
        self.filter_menu.bind("<<ComboboxSelected>>", self.update_filter)

        self.quit_button = tk.Button(root, text="Quit", command=self.quit_app)
        self.quit_button.pack()

        self.update_video()
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

    def update_filter(self, event):
        selected_filter = self.filter_var.get()
        self.video_processor.set_filter(selected_filter)

    def update_video(self):
        frame = self.video_processor.get_frame()
        if frame is not None:
            frame = Image.fromarray(frame)
            frame = ImageTk.PhotoImage(frame)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=frame)
            self.canvas.image = frame
        self.root.after(10, self.update_video)

    def quit_app(self):
        self.video_processor.release()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoApp(root)
    root.mainloop()
