from flask import Flask, send_from_directory

app = Flask(__name__)


@app.route("/webapp")
def webapp():
    return send_from_directory(
        "webapp",
        "index.html"
    )


@app.route("/webapp/<path:path>")
def files(path):
    return send_from_directory(
        "webapp",
        path
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )