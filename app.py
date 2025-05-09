from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "this is from code-server website for python flask ok"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=6666)