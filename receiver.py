import cv2
import socket
import pickle
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from video import VideoProcessor

class Receiver:
    def __init__(self, root, sender_ip="192.168.43.225", recv_port=5000, send_port=5001):
        self.root = root
        self.root.title("Video Call - Receiver")
        self.processor = VideoProcessor()

        # Setup sockets
        self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1000000)
        self.recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1000000)
        self.sender_ip = sender_ip
        self.recv_port = recv_port
        self.send_port = send_port
        self.running = True

        # UI Components
        self.local_canvas = tk.Canvas(root, width=600, height=600)
        self.local_canvas.pack(side=tk.LEFT, padx=10, pady=10)

        self.remote_canvas = tk.Canvas(root, width=600, height=600)
        self.remote_canvas.pack(side=tk.RIGHT, padx=10, pady=10)

        self.filter_label = tk.Label(root, text="Choose a Filter:")
        self.filter_label.pack()

        self.filter_var = tk.StringVar(value="none")
        self.filter_menu = ttk.Combobox(root, textvariable=self.filter_var, 
                                        values=["none", "hat", "mustache"," sunglass","flower_crown","beard","butterfly"], state="readonly")
        self.filter_menu.pack()
        self.filter_menu.bind("<<ComboboxSelected>>", self.update_filter)

        self.quit_button = tk.Button(root, text="Quit", command=self.quit_app)
        self.quit_button.pack()

        # Start Threads
        threading.Thread(target=self.send_video, daemon=True).start()
        threading.Thread(target=self.receive_video, daemon=True).start()

        # Update Video
        self.update_video()
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

    def update_filter(self, event):
        selected_filter = self.filter_var.get()
        self.processor.set_filter(selected_filter)

    def send_video(self):
        while self.running:
            frame = self.processor.get_frame()
            if frame is None:
                continue
            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 30])
            data = pickle.dumps(buffer)
            self.send_sock.sendto(data, (self.sender_ip, self.send_port))

    def receive_video(self):
        self.recv_sock.bind(("", self.recv_port))
        while self.running:
            try:
                data, _ = self.recv_sock.recvfrom(65535)
                buffer = pickle.loads(data)
                frame = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
                if frame is not None:
                    self.update_remote_video(frame)
            except Exception as e:
                print(f"Receiver error: {e}")

    def update_video(self):
        frame = self.processor.get_frame()
        if frame is not None:
            frame = Image.fromarray(frame)
            frame = ImageTk.PhotoImage(frame)
            self.local_canvas.create_image(0, 0, anchor=tk.NW, image=frame)
            self.local_canvas.image = frame
        self.root.after(10, self.update_video)

    def update_remote_video(self, frame):
        frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        frame = ImageTk.PhotoImage(frame)
        self.remote_canvas.create_image(0, 0, anchor=tk.NW, image=frame)
        self.remote_canvas.image = frame

    def quit_app(self):
        self.running = False
        self.processor.release()
        self.send_sock.close()
        self.recv_sock.close()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    receiver = Receiver(root, sender_ip="192.168.43.225")
    root.mainloop()
