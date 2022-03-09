import flask
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS


app = Flask(__name__)
#CORS(app)

@app.get("/")

def index_get():
    return render_template("base.html") 


@app.post("/predict")
def predict():
    # get user input
    response = "Sorry, I can't do anything right now lol" # get bot output from back-end
    message = {"answer": response}
    return jsonify(message)

if __name__ == "__main__":
    app.run(debug=True)


