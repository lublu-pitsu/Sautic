from flask import Flask

app = Flask(__name__)

@app.route('/')
def log():
    return template("log_t.html")

if __name__ == '__main__':
    app.run()