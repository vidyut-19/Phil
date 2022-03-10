import flask
from flask import Flask, render_template, request, jsonify
#from flask_cors import CORS
from sel import get_course_eval

app = Flask(__name__)
#CORS(app)

@app.get("/")

def index_get():
    return render_template("base.html") 

@app.post("/predict")
def predict():
    # get user input
    #response = get_response(user_input)
    text = request.get_json().get("message")
    # error check --> if text is valid
    response = get_course_eval(text)  # get bot output from back-end
    message = {"answer": response}
    return jsonify(message)


if __name__ == "__main__":
    app.run(debug=True)


