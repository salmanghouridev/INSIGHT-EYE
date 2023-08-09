from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/api/python")
def fdata():
    data = [
        {
            'title': 'This is one',
            'status': 'success'
        },
        {
            'title': 'This is two',
            'status': 'success'
        },
        {
            'title': 'This is three',
            'status': 'success'
        }
    ]
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
