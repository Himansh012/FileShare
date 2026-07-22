from flask import Flask, render_template, request
import pathlib

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods = ["POST"])
def upload():
    # print(request.files)
    uploaded_file = request.files["file"]
    print(type(uploaded_file))
    print(uploaded_file.filename)
    print(uploaded_file.content_type)

    print(dir(uploaded_file))
    return home()


if __name__ == "__main__":
    app.run(debug=True)