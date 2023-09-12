from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import dlib

app = Flask(__name__)

# Load the pre-trained model
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
detector = dlib.get_frontal_face_detector()

# Global variables to store Snellen chart words and current index
snellen_chart = ["E", "F", "P", "T", "O", "L", "C", "D", "Z", "V"]
current_word_index = 0

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_next_word', methods=['GET'])
def get_next_word():
    global current_word_index
    word = snellen_chart[current_word_index]
    current_word_index = (current_word_index + 1) % len(snellen_chart)
    return jsonify({'word': word})

@app.route('/verify_word', methods=['POST'])
def verify_word():
    global current_word_index
    user_response = request.form['response']
    correct_word = snellen_chart[current_word_index - 1]
    verification_status = user_response.strip().upper() == correct_word.strip().upper()
    return jsonify({'verified': verification_status})

@app.route('/process_image', methods=['POST'])
def process_image():
    img_data = request.files['image'].read()
    img = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_UNCHANGED)

    # detect faces in the image
    faces = detector(img)

    response_data = {}
    if faces:
        # Get landmarks of the first face detected
        landmarks = predictor(img, faces[0])

        # Calculate the distance between two eye landmarks (for instance, points 36 and 45)
        pointLeft = (landmarks.part(36).x, landmarks.part(36).y)
        pointRight = (landmarks.part(45).x, landmarks.part(45).y)

        w = ((pointRight[0] - pointLeft[0])**2 + (pointRight[1] - pointLeft[1])**2) ** 0.5
        W = 6.3  # average pupillary distance in cm
        f = 590  # focal length of the webcam (you may need to adjust this)
        d_cm = (W * f) / w
        d_inch = d_cm / 2.54

        response_data = {
            'distance': int(d_inch)
        }

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)
