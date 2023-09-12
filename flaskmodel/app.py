from flask import Flask, render_template, request, jsonify
import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
import numpy as np

app = Flask(__name__)

# Initialize the detector
detector = FaceMeshDetector(maxFaces=1)

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
    img = cv2.imdecode(np.fromstring(img_data, np.uint8), cv2.IMREAD_UNCHANGED)

    # Your existing code for processing the image goes here...
    img, faces = detector.findFaceMesh(img, draw=False)
    
    response_data = {}
    if faces:
        face = faces[0]
        pointLeft = face[145]
        pointRight = face[374]
        
        w, _ = detector.findDistance(pointLeft, pointRight)
        W = 6.3
        f = 590
        d_cm = (W * f) / w
        d_inch = d_cm / 2.54
        
        response_data = {
            'distance': int(d_inch)
        }

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)
