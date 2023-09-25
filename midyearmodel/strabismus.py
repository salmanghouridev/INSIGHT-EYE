from flask import Blueprint, render_template, Response, jsonify
import cv2
import dlib
import math
import os
import time
from flask import flash, redirect, url_for
from tkinter import messagebox

strabismus = Blueprint('strabismus', __name__)

# Initialize face detector and shape predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

class RealTimeStrabismusDetectionApp:
    def __init__(self):
        self.video_capture = cv2.VideoCapture(0)
        self.angle = 0.0
        self.vertical_displacement = 0.0
        self.latest_report = ""
        self.capture_flag = False  # Flag to trigger capture

    def process_image(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)
        report = "No face detected"
        
        img_with_points = img.copy()

        for face in faces:
            landmarks = predictor(gray, face)
            left_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)]
            right_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)]

            left_eye_center = self.calculate_eye_center(left_eye)
            right_eye_center = self.calculate_eye_center(right_eye)
            self.angle = self.calculate_angle(left_eye_center, right_eye_center)
            self.vertical_displacement = self.calculate_vertical_displacement(left_eye_center, right_eye_center)

            prediction = self.predict_strabismus_type(self.angle, self.vertical_displacement)

            cv2.line(img_with_points, left_eye_center, right_eye_center, (255, 0, 0), 1)
            cv2.circle(img_with_points, left_eye_center, 2, (0, 0, 255), 0)
            cv2.circle(img_with_points, right_eye_center, 2, (0, 0, 255), 0)

            for eye_points in [left_eye, right_eye]:
                for point in eye_points:
                    cv2.circle(img_with_points, point, 1, (0, 255, 0), -2)

            report = f"The calculated angle is: {self.angle:.2f} degrees.\n"\
                     f"The calculated vertical displacement is: {self.vertical_displacement:.2f} pixels.\n"\
                     f"Predicted strabismus type: {prediction}"
            self.latest_report = report

            # Automatically capture and save the image if angle and vertical displacement are both 0.00
            if self.angle == 0.00 and self.vertical_displacement == 0.00 and not self.capture_flag:
                self.capture_flag = True
                self.capture_frame()

        return img_with_points, report

    def calculate_eye_center(self, eye_points):
        x_coords = [point[0] for point in eye_points]
        y_coords = [point[1] for point in eye_points]
        return sum(x_coords) // len(x_coords), sum(y_coords) // len(y_coords)

    def calculate_angle(self, left_eye_center, right_eye_center):
        delta_x = right_eye_center[0] - left_eye_center[0]
        delta_y = right_eye_center[1] - left_eye_center[1]
        return math.degrees(math.atan2(delta_y, delta_x))

    def calculate_vertical_displacement(self, left_eye_center, right_eye_center):
        return left_eye_center[1] - right_eye_center[1]

# def predict_strabismus_type(self, angle, vertical_displacement):
#         if abs(angle) > 8:
#             if angle > 8:
#                 return "Esotropia"
#             elif angle < -8:
#                 return "Exotropia"
#         elif abs(vertical_displacement) > 5:
#             if vertical_displacement > 5:
#                 return "Hypertropia"
#             elif vertical_displacement < -5:
#                 return "Hypotropia"
#         else:
#             return "None"

    def predict_strabismus_type(self, angle, vertical_displacement):
        # Thresholds for diagnosing strabismus based on angle and vertical displacement
        angle_threshold = 8  # degrees
        displacement_threshold = 5  # millimeters or degrees

        if abs(angle) > angle_threshold:
            if angle > 0:
                return "Esotropia"  # Inward deviation
            elif angle < 0:
                return "Exotropia"  # Outward deviation

        elif abs(vertical_displacement) > displacement_threshold:
            if vertical_displacement > 0:
                return "Hypertropia"  # Upward displacement
            elif vertical_displacement < 0:
                return "Hypotropia"  # Downward displacement
        else:
            return "None"  # No significant strabismus detected


    def generate_frames(self):
        while True:
            ret, frame = self.video_capture.read()
            if not ret:
                break

            frame, report = self.process_image(frame)
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def capture_frame(self):
        """Capture and save the current frame with points and lines, and save the report."""
        try:
            ret, frame = self.video_capture.read()
            if not ret:
                return

            # Process the frame to detect eyes and draw points and lines
            frame_with_points, report = self.process_image(frame)

            # Specify the directory path where you want to save the files
            base_dir = r"D:\Projects\Final Year Project\Flask 2 - Copy\Cap"  # Use a raw string to handle backslashes

            # Find the existing report folders and determine the next folder name
            existing_folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]
            report_numbers = [int(folder[len("report_"):]) for folder in existing_folders if folder.startswith("report_")]
            
            next_report_number = max(report_numbers) + 1 if report_numbers else 1

            # Create the new report folder
            report_folder = os.path.join(base_dir, f"report_{next_report_number:03}")
            os.makedirs(report_folder, exist_ok=True)

            # Save the frame with points and lines as an image file
            timestamp = time.strftime("%Y%m%d%H%M%S")
            filename = f"captured_frame_with_points_{timestamp}.png"
            save_path = os.path.join(report_folder, filename)
            cv2.imwrite(save_path, frame_with_points)

            # Save the report to a text file
            report_filename = "captured_frame_report.txt"
            report_save_path = os.path.join(report_folder, report_filename)
            with open(report_save_path, "w") as report_file:
                report_file.write(report)

            # Show a message box to confirm the capture
            messagebox.showinfo("Capture", f"Frame with points and lines and report saved in '{report_folder}'")

            # Shut down the camera
            self.shutdown_camera()

            # flash(f"Frame with points and lines and report saved in '{report_folder}'", 'success')

            # Redirect to the dashboard
            return redirect(url_for('dashboard.index2'))

        except Exception as e:
            flash(f"Error: {str(e)}", 'error')
            return redirect(url_for('dashboard.html'))

    def shutdown_camera(self):
        if self.video_capture.isOpened():
            self.video_capture.release()


def video_feed():
    strabismus.detector_app = RealTimeStrabismusDetectionApp()
    return Response(strabismus.detector_app.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@strabismus.route('/')
def index2():
    return render_template('astrabismus.html')

@strabismus.route('/startingpage_Strabismus')
def indexlanding():
    return render_template('strabismus2.html')


@strabismus.route('/video_feeds')
def video_feed_route():
    return video_feed()


@strabismus.route('/get_latest_report')
def get_latest_report():
    if hasattr(strabismus, 'detector_app'):
        return jsonify(report=strabismus.detector_app.latest_report)
    else:
        return jsonify(report="No data available")


@strabismus.route('/capture_alert/<message>')
def capture_alert(message):
    # Display the capture alert message on the HTML page
    return render_template('astrabismus.html', capture_alert_message=message)

@strabismus.route('/shutdown', methods=['GET'])
def shutdown():
    # Gracefully shutdown the Flask app
    shutdown_video_feed()
    return redirect('/dashboard')


def shutdown_video_feed():
    # Perform any cleanup or shutdown tasks here
    print("Shutting down the video feed gracefully")
    if hasattr(strabismus, 'detector_app'):
        strabismus.detector_app.video_capture.release()

# def shutdown_server():
#     # Shut down the camera
#     if hasattr(strabismus, 'detector_app'):
#         strabismus.detector_app.shutdown_camera()

#     # Perform any other cleanup or shutdown tasks here
#     print("Shutting down the server gracefully")
#     os._exit(0)  # Exit the application

