from flask import Blueprint, render_template, send_from_directory, request, jsonify

color_blindness = Blueprint('color_blindness', __name__)

image_data = [
    {"path": "image1.png", "answer": ["7.", "seven", "s e v e n"]},
    {"path": "image2.png", "answer": ["4.", "four", "f o u r"]},
    {"path": "image3.png", "answer": ["3.", "three", "t h r e e"]},
    {"path": "image4.png", "answer": ["4.", "four", "f o u r"]},
    {"path": "image5.png", "answer": ["9.", "nine", "n i n e"]}, 
]

@color_blindness.route('/get_image/<int:image_index>')
def get_image(image_index):
    image_info = image_data[image_index]
    return send_from_directory('static/colorimages', image_info['path'])

@color_blindness.route('/validate_answer', methods=['POST'])
def validate_answer():
    data = request.json
    image_index = data['image_index']
    user_answer = data['user_answer'].lower().strip()
    
    # Check if the user's answer is in the list of correct answers for the image
    correct_answers = image_data[image_index]["answer"]
    
    if user_answer in correct_answers:
        is_correct = True
    else:
        is_correct = False
    
    return jsonify(is_correct=is_correct)

@color_blindness.route('/')
def image_home():
    return render_template('colorblindness.html', total_questions=len(image_data))

@color_blindness.route('/colorblindnesspage')
def image_home2():
    return render_template('colorblindness2.html', total_questions=len(image_data))
