from flask import Flask, render_template, request, redirect, url_for, flash, session, Response, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from Levenshtein import distance
import dlib
import math
import os
import time
from tkinter import messagebox
import cv2
import numpy as np
import pandas as pd
from strabismus import strabismus
from color_blindness import color_blindness
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector


app = Flask(__name__)
cap = cv2.VideoCapture(0)
detector = FaceMeshDetector(maxFaces=1)

app.register_blueprint(color_blindness, url_prefix='/color_blindness')
app.register_blueprint(strabismus, url_prefix='/strabismus')


app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/mydatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


@app.route('/')
def home():
    return redirect(url_for('home1'))


depth_inches = 0
cap = None

# snell chart


snell_chart_data = [
    {
        "Letter": "E",
        "Possibilities": ["E.", "E For Elephant"],
        "Font Size (mm)": 11.3,
        "Font Size (px)": 39,
        "Snellen Fraction": "20/20",
        "Approx. Visual Acuity": "Normal Vision",
        "Spherical Lens (Diopters)": "0.00 D",
        "Cylindrical Lens (Diopters)": "0.00 D",
        "Estimated Refraction Status": "SPH: 0.00 D, CYL: 0.00 D, Axis: N/A",
        "Add Power for Presbyopia (Diopters)": "0.00 D",
        "Prism Correction (Prism Diopters)": "0 Prism Diopters",
        "Potential Eye Conditions": "Normal Vision",
        "Recommendations & Prescriptions": "No correction needed",
        "Lighting Conditions": "Adequate Lighting",
        "Total Distance (cm)": 100,
        "Additional Descriptions": "Your eyes are in great condition!"
    },
    {
        "Letter": "T O Z",
        "Possibilities": ["T O Z.", "TOZ", "T OZ.", "T OZ.", "TOZ."],
        "Font Size (mm)": 7.5,
        "Font Size (px)": 24,
        "Snellen Fraction": "20/30",
        "Approx. Visual Acuity": "Mildly Reduced",
        "Spherical Lens (Diopters)": "-0.50 to +0.50 D",
        "Cylindrical Lens (Diopters)": "-0.50 to +0.75 D",
        "Estimated Refraction Status": "SPH: ±0.50 D, CYL: ±0.75 D, Axis: Varies",
        "Add Power for Presbyopia (Diopters)": "±0.50 D",
        "Prism Correction (Prism Diopters)": "0-2 Prism Diopters",
        "Potential Eye Conditions": "Myopia",
        "Recommendations & Prescriptions": "Consider corrective lenses",
        "Lighting Conditions": "Adequate to Dim",
        "Total Distance (cm)": 100,
        "Additional Descriptions": "Consider a check-up to avoid potential issues."
    },
    {
        "Letter": "L P E D",
        "Possibilities": ["L PED.", "LP ED.", "L P ED.", "LPED.", "L P E D.", "LPE D.", "L PE D.", "L PED. "],
        "Font Size (mm)": 6.0,
        "Font Size (px)": 20,
        "Snellen Fraction": "20/40",
        "Approx. Visual Acuity": "Reduced",
        "Spherical Lens (Diopters)": "-0.75 to +0.75 D",
        "Cylindrical Lens (Diopters)": "-0.75 to +1.00 D",
        "Estimated Refraction Status": "SPH: ±0.75 D, CYL: ±1.00 D, Axis: Varies",
        "Add Power for Presbyopia (Diopters)": "±0.75 D",
        "Prism Correction (Prism Diopters)": "1-2 Prism Diopters",
        "Potential Eye Conditions": "Hyperopia",
        "Recommendations & Prescriptions": "Prescribe corrective lenses",
        "Lighting Conditions": "Adequate to Dim",
        "Total Distance (cm)": 100,
        "Additional Descriptions": "Corrective lenses might enhance your vision."
    },
    {
        "Letter": "P E C F D",
        "Possibilities": ["P E C F D.", "P ECFD.", "PE C F D.", "PECF D.", "PE CFD", "P E CFD.", "P ECF D.", "PECFD."],
        "Font Size (mm)": 5.4,
        "Font Size (px)": 18,
        "Snellen Fraction": "20/50",
        "Approx. Visual Acuity": "Noticeably Reduced",
        "Spherical Lens (Diopters)": "-1.00 to +1.00 D",
        "Cylindrical Lens (Diopters)": "-1.00 to +1.50 D",
        "Estimated Refraction Status": "SPH: ±1.00 D, CYL: ±1.50 D, Axis: Varies",
        "Add Power for Presbyopia (Diopters)": "±1.00 D",
        "Prism Correction (Prism Diopters)": "2-3 Prism Diopters",
        "Potential Eye Conditions": "Astigmatism",
        "Recommendations & Prescriptions": "Prescribe higher power lenses",
        "Lighting Conditions": "Dim Lighting",
        "Total Distance (cm)": 100,
        "Additional Descriptions": "Higher power lenses might be necessary."
    },
    {
        "Letter": "E D F C Z P",
        "Possibilities": ["E D F C Z P.", "E DFCZP.", "ED F C Z P.", "EDFC Z P."],
        "Font Size (mm)": 4.5,
        "Font Size (px)": 14,
        "Snellen Fraction": "20/70",
        "Approx. Visual Acuity": "Poor Vision",
        "Spherical Lens (Diopters)": "-1.50 to +1.50 D",
        "Cylindrical Lens (Diopters)": "-1.50 to +2.00 D",
        "Estimated Refraction Status": "SPH: ±1.50 D, CYL: ±2.00 D, Axis: Varies",
        "Add Power for Presbyopia (Diopters)": "±1.25 D",
        "Prism Correction (Prism Diopters)": "3-4 Prism Diopters",
        "Potential Eye Conditions": "Presbyopia",
        "Recommendations & Prescriptions": "Recommend multifocal lenses",
        "Lighting Conditions": "Dim to Low Lighting",
        "Total Distance (cm)": 100,
        "Additional Descriptions": "Multifocal lenses might be beneficial."
    },
    {
        "Letter": "F E L O P Z D",
        "Possibilities": ["F E L O P Z D.", "F ELOPZD.", "FE L O P Z D.", "FELO P Z D."],
        "Font Size (mm)": 3.8,
        "Font Size (px)": 12,
        "Snellen Fraction": "20/100",
        "Approx. Visual Acuity": "Very Poor Vision",
        "Spherical Lens (Diopters)": "-2.00 to +2.00 D",
        "Cylindrical Lens (Diopters)": "-2.00 to +2.50 D",
        "Estimated Refraction Status": "SPH: ±2.00 D, CYL: ±2.50 D, Axis: Varies",
        "Add Power for Presbyopia (Diopters)": "±1.50 D",
        "Prism Correction (Prism Diopters)": "4-5 Prism Diopters",
        "Potential Eye Conditions": "Advanced Presbyopia",
        "Recommendations & Prescriptions": "Recommend high power multifocal lenses",
        "Lighting Conditions": "Low Lighting",
        "Total Distance (cm)": 100,
        "Additional Descriptions": "High power lenses can aid in improving vision."
    },
    {
        "Letter": "D E F P O T E C",
        "Possibilities": ["D E F P O T E C.", "D EF POTEC.", "DE F P O T E C.", "DEF P O T EC."],
        "Font Size (mm)": 3.1,
        "Font Size (px)": 11,
        "Snellen Fraction": "20/200",
        "Approx. Visual Acuity": "Severely Reduced",
        "Spherical Lens (Diopters)": "-2.50 to +2.50 D",
        "Cylindrical Lens (Diopters)": "-2.50 to +3.00 D",
        "Estimated Refraction Status": "SPH: ±2.50 D, CYL: ±3.00 D, Axis: Varies",
        "Add Power for Presbyopia (Diopters)": "±1.75 D",
        "Prism Correction (Prism Diopters)": "5-6 Prism Diopters",
        "Potential Eye Conditions": "Advanced Cataract",
        "Recommendations & Prescriptions": "Recommend surgery consultation",
        "Lighting Conditions": "Low Lighting",
        "Total Distance (cm)": 100,
        "Additional Descriptions": "A surgery consultation might be necessary."
    },
    {
        "Letter": "L E F O D P C T",
        "Possibilities": ["L E F O D P C T.", "L EF O DPC T.", "LE F O DP C T.", "LEF O D PC T."],
        "Font Size (mm)": 2.7,
        "Font Size (px)": 9,
        "Snellen Fraction": "20/400",
        "Approx. Visual Acuity": "Extremely Poor Vision",
        "Spherical Lens (Diopters)": "-3.00 to +3.00 D",
        "Cylindrical Lens (Diopters)": "-3.00 to +3.50 D",
        "Estimated Refraction Status": "SPH: ±3.00 D, CYL: ±3.50 D, Axis: Varies",
        "Add Power for Presbyopia (Diopters)": "±2.00 D",
        "Prism Correction (Prism Diopters)": "6-8 Prism Diopters",
        "Potential Eye Conditions": "Glaucoma",
        "Recommendations & Prescriptions": "Consult for potential surgery",
        "Lighting Conditions": "Low to Very Low Lighting",
        "Total Distance (cm)": 100,
        "Additional Descriptions": "A consult for potential surgery might be necessary."
    },
    {
        "Letter": "F D P L T C E O",
        "Possibilities": ["F D P L T C E O.", "F DPLTC EO.", "FD P L T C E O.", "FDP L T C E O."],
        "Font Size (mm)": 2.3,
        "Font Size (px)": 7,
        "Snellen Fraction": "20/800",
        "Approx. Visual Acuity": "Nearly Blind",
        "Spherical Lens (Diopters)": "Consult a professional",
        "Cylindrical Lens (Diopters)": "Consult a professional",
        "Estimated Refraction Status": "SPH: ±3.50 D or higher, CYL: ±4.00 D or higher, Axis: Varies",
        "Add Power for Presbyopia (Diopters)": "Consult a professional",
        "Prism Correction (Prism Diopters)": "Consult a professional",
        "Potential Eye Conditions": "Severe Retinal Disease",
        "Recommendations & Prescriptions": "Urgent consultation with a specialist",
        "Lighting Conditions": "Very Low Lighting",
        "Total Distance (cm)": 100,
        "Additional Descriptions": "Urgent consultation required to assess potential treatment options."
    },
    {
        "Letter": "P E T O L C F T D",
        "Possibilities": ["P E T O L C F T D", "P ETO LCFTD", "PET O LCFT D", "PETO L CFT D"],
        "Font Size (mm)": 2.3,
        "Font Size (px)": 4,
        "Snellen Fraction": "20/1000",
        "Approx. Visual Acuity": "Nearly Blind",
        "Spherical Lens (Diopters)": "Consult a professional",
        "Cylindrical Lens (Diopters)": "Consult a professional",
        "Estimated Refraction Status": "SPH: ±3.50 D or higher, CYL: ±4.00 D or higher, Axis: Varies",
        "Add Power for Presbyopia (Diopters)": "Consult a professional",
        "Prism Correction (Prism Diopters)": "Consult a professional",
        "Potential Eye Conditions": "Severe Retinal Disease",
        "Recommendations & Prescriptions": "Urgent consultation with a specialist",
        "Lighting Conditions": "Very Low Lighting",
        "Total Distance (cm)": 100,
        "Additional Descriptions": "Urgent consultation required to assess potential treatment options."
    },
    {
        "Letter": "Not Visible",
        "Possibilities": ["Not Visible", "Invisible"],
        "Font Size (mm)": "N/A",
        "Font Size (px)": 3,
        "Snellen Fraction": "N/A",
        "Approx. Visual Acuity": "No Vision",
        "Spherical Lens (Diopters)": "Consult a professional",
        "Cylindrical Lens (Diopters)": "Consult a professional",
        "Estimated Refraction Status": "Consult a professional",
        "Add Power for Presbyopia (Diopters)": "Consult a professional",
        "Prism Correction (Prism Diopters)": "Consult a professional",
        "Potential Eye Conditions": "Complete Vision Loss",
        "Recommendations & Prescriptions": "Urgent consultation with a specialist",
        "Lighting Conditions": "Variable",
        "Total Distance (cm)": 100,
        "Additional Descriptions": "Immediate medical attention required."
    }
]

# Global variables
current_word_index = 0
incorrect_attempts = {i: 0 for i in range(len(snell_chart_data))}
distance_cm_global = 0


def is_input_correct(user_input, expected_input):
    return re.sub(r'[^a-zA-Z]', '', user_input).lower() == expected_input.lower()


@app.route('/snellen_chart_test')
def index():
    global current_word_index
    global incorrect_attempts
    global cap
    initial_message = "Hello! Welcome to the eye test. Click the microphone button to start or stop the voice listener. When ready, please read the first letter displayed on the Snellen chart."

    current_word_index = 0
    incorrect_attempts = {i: 0 for i in range(len(snell_chart_data))}
    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(0)
    return render_template('index.html', data=snell_chart_data[current_word_index], initial_message=initial_message)


#
def generate_report_table(word_index):
    if word_index >= 0 and word_index < len(snell_chart_data):
        word_data = snell_chart_data[word_index]
        report_html = '<div id="report-table"><table><tr>'
        for key in word_data:
            if key != "Letter":
                report_html += '<th>' + key + '</th>'
        report_html += '</tr><tr>'
        for key in word_data:
            if key != "Letter":
                report_html += '<td>' + str(word_data[key]) + '</td>'
        report_html += '</tr></table></div>'
        return report_html
    else:
        return ""


@app.route('/check-input', methods=['POST'])
def check_input():
    global current_word_index
    global incorrect_attempts

    user_input = request.form['user_input'].strip()

    if current_word_index < len(snell_chart_data):
        expected_input = snell_chart_data[current_word_index]["Possibilities"]

        if user_input in expected_input:
            incorrect_attempts[current_word_index] = 0
            current_word_index += 1
            response_text = "Correct!"
            next_data = snell_chart_data[current_word_index] if current_word_index < len(
                snell_chart_data) else None

            # Store the user's input and correctness in the data dictionary
            snell_chart_data[current_word_index - 1]['user_input'] = user_input
            snell_chart_data[current_word_index - 1]['correct'] = True
        else:
            incorrect_attempts[current_word_index] += 1

            if incorrect_attempts[current_word_index] >= 3:
                response_text = f"That seems challenging. The correct input was one of: {', '.join(expected_input)}. Let's move to the next one."
                next_data = snell_chart_data[current_word_index] if current_word_index < len(
                    snell_chart_data) else None

                # Store the user's input and correctness in the data dictionary
                snell_chart_data[current_word_index]['user_input'] = user_input
                snell_chart_data[current_word_index]['correct'] = False

                # Generate and append the report table HTML for the word
                report_table = generate_report_table(current_word_index)
                if report_table:
                    response_text += report_table
                    next_data = snell_chart_data[current_word_index] if current_word_index < len(
                        snell_chart_data) else None
            else:
                response_text = f"Try again. (Attempt {incorrect_attempts[current_word_index]})"
                next_data = None
    else:
        response_text = "Test completed. Thank you!"
        next_data = None

    response_voice = response_text

    return jsonify({'response_text': response_text, 'response_voice': response_voice, 'next_data': next_data})

# end


def generate_frames():
    while True:
        success, img = cap.read()
        img, faces = detector.findFaceMesh(img, draw=False)

        if faces:
            face = faces[0]
            pointLeft = face[145]
            pointRight = face[374]
            cv2.circle(img, pointLeft, 4, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, pointRight, 4, (255, 0, 255), cv2.FILLED)
            w, _ = detector.findDistance(pointLeft, pointRight)
            W = 6.3

            f = 590
            d_cm = (W * f) / w
            d_inch = d_cm / 2.54  # Convert cm to inches

            global depth_inches
            depth_inches = int(d_inch)

            depth_text = f'Depth: {depth_inches} inches'

        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/get_distance', methods=['GET'])
def get_distance():
    global depth_inches
    return jsonify({'depth': depth_inches})


@app.route('/close_camera', methods=['POST'])
def close_camera():
    global cap
    if cap is not None and cap.isOpened():
        cap.release()
    cv2.destroyAllWindows()

    return redirect(url_for('dashboard'))


@app.route('/home')
def home1():
    return render_template('home.html')


@app .route('/about')
def about():
    return render_template('about.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# modelend


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration Successful')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login Successful')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Username or Password')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login first')
        return redirect(url_for('login'))

    return render_template('dashboard.html')


@app.route('/test')
def test():
    if 'user_id' not in session:
        flash('Please login first')
        return redirect(url_for('login'))

    return render_template('test.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)