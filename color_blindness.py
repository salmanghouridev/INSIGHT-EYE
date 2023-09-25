from flask import Blueprint, render_template, send_from_directory, request, jsonify
from Levenshtein import distance

color_blindness = Blueprint('color_blindness', __name__)

image_data = [
    {"path": "image1.png", "answer": "s e v e n"},
    {"path": "image2.png", "answer": "f o u r"},
    {"path": "image3.png", "answer": "t h r e e"},
    {"path": "image4.png", "answer": "f o u r"},
    {"path": "image5.png", "answer": "n i n e"},
]

@color_blindness.route('/get_image/<int:image_index>')
def get_image(image_index):
    image_info = image_data[image_index]
    return send_from_directory('static/colorimages', image_info['path'])

number_to_word = {
    "1": "one", "2": "two", "3": "three", 
    "4": "four", "5": "five", "6": "six", 
    "7": "seven", "8": "eight", "9": "nine"
}

@color_blindness.route('/validate_answer', methods=['POST'])
def validate_answer():
    data = request.json
    image_index = data['image_index']
    user_answer = data['user_answer'].lower().strip()

    correct_answer = str(image_data[image_index]["answer"]).lower().strip()

    if correct_answer in number_to_word:
        correct_answer_word = number_to_word[correct_answer]
    else:
        correct_answer_word = correct_answer

    lev_distance = min(distance(user_answer, correct_answer), distance(user_answer, correct_answer_word))
    distance_threshold = 2

    is_correct = lev_distance <= distance_threshold
    return jsonify(is_correct=is_correct)

@color_blindness.route('/')
def image_home():
    return render_template('colorblindness.html', total_questions=len(image_data))
