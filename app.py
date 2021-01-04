import os
from flask import Flask
if os.path.exists("env.py"):
    import env

# create an instance of Flask (stored in variable named "app")
app = Flask(__name__)


@app.route("/")
def hello():
    return "hello world ... again"


# tell application how and where to run
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
